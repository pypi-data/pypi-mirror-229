# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import multiprocessing
import os
import signal
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime
from pathlib import Path
from typing import Dict

from flask import Flask, Response, g, jsonify, request

from promptflow._internal import (
    VERSION,
    ErrorResponse,
    ExceptionPresenter,
    JsonSerializedPromptflowException,
    OperationContext,
    _change_working_dir,
    collect_package_tools,
    generate_prompt_meta,
    generate_python_meta,
    generate_tool_meta_dict_by_file,
    inject_sys_path,
)
from promptflow._legacy.legacy_run_tracker import LegacyRunTracker
from promptflow._legacy.runtime_utils import get_log_context
from promptflow.contracts.run_mode import RunMode
from promptflow.contracts.tool import ToolType
from promptflow.runtime.constants import SYNC_REQUEST_TIMEOUT_THRESHOLD
from promptflow.runtime.contracts._errors import InvalidFlowSourceType
from promptflow.runtime.contracts.runtime import (
    BulkRunRequestV2,
    FlowRequestV2,
    FlowSourceType,
    MetaV2Request,
    SingleNodeRequestV2,
    SubmitFlowRequest,
)
from promptflow.runtime.data import prepare_blob_directory
from promptflow.runtime.utils._debug_log_helper import generate_safe_error_stacktrace
from promptflow.runtime.utils._run_status_helper import mark_run_as_preparing_in_runhistory
from promptflow.runtime.utils.internal_logger_utils import (
    TelemetryLogHandler,
    set_custom_dimensions_to_logger,
    system_logger,
)
from promptflow.runtime.utils.run_result_parser import RunResultParser

from ._errors import GenerateMetaTimeout, NoToolTypeDefined, RuntimeTerminatedByUser
from .runtime import (
    PromptFlowRuntime,
    execute_bulk_run_request,
    execute_flow_request,
    execute_node_request,
    get_log_context_from_v2_request,
    reset_and_close_logger,
)
from .runtime_config import load_runtime_config
from .utils import logger, multi_processing_exception_wrapper, setup_contextvar
from .utils._flow_source_helper import fill_working_dir

app = Flask(__name__)

active_flow_request_context = ContextVar("SubmitFlowRequest", default=None)
collect_package_tools()  # Collect package tools when runtime starts to avoid loading latency in each request.


def signal_handler(signum, frame):
    signame = signal.Signals(signum).name
    logger.info("Runtime stopping. Handling signal %s (%s)", signame, signum)
    try:
        flow_request: SubmitFlowRequest = active_flow_request_context.get()
        run_tracker = LegacyRunTracker.active_instance()
        if flow_request is not None and isinstance(run_tracker, LegacyRunTracker):
            flow_id = flow_request.flow_id
            all_run_ids = flow_request.get_root_run_ids()
            logger.info("Update flow runs to failed on exit. Flow id: %s, root run ids: %s", flow_id, all_run_ids)
            ex = RuntimeTerminatedByUser(
                f"Flow run failed because runtime is terminated at {datetime.utcnow().isoformat()}. "
                f"It may be caused by runtime version update or compute instance stop."
            )
            # Update active runs to failed first, then not started runs.
            # Because mark_notstarted_runs_as_failed may start new run, we may meet mlflow error
            # "To start a new run, first end the current run with mlflow.end_run()." if there's active run.
            run_tracker.mark_active_runs_as_failed_on_exit(root_run_ids=all_run_ids, ex=ex)
            run_tracker.mark_notstarted_runs_as_failed(flow_id=flow_id, root_run_ids=all_run_ids, ex=ex)
    except Exception:
        logger.warning("Error when handling runtime stop signal", exc_info=True)
    finally:
        sys.exit(1)


# register signal handler to gracefully shutdown
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


@app.errorhandler(Exception)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors with correct error code & error category."""

    resp = generate_error_response(e)

    return jsonify(resp.to_dict()), resp.response_code


@app.before_request
def setup_logger():
    """Setup operation context and logger context."""
    # Record request info in global context.
    g.method = request.method
    g.url = request.url
    g.entry_time = datetime.utcnow()
    # Setup operation context.

    runtime: PromptFlowRuntime = PromptFlowRuntime.get_instance()
    runtime.update_operation_context(request)
    # Set logger context.
    custom_dimensions = get_custom_dimensions()
    for handler in logger.handlers:
        if isinstance(handler, TelemetryLogHandler):
            handler.set_or_update_context(custom_dimensions)

    logger.info("Receiving request [method=%s] [url=%s]", g.method, g.url)


@app.after_request
def teardown_logger(response: Response):
    """Clear logger context."""
    duration_ms = (datetime.utcnow() - g.entry_time).total_seconds() * 1000  # Unit is milliseconds.
    logger.info(
        "Request finishes [status=%s] [duration(ms)=%s] [method=%s] [url=%s]",
        response.status_code,
        duration_ms,
        g.method,
        g.url,
    )

    for handler in logger.handlers:
        if isinstance(handler, TelemetryLogHandler):
            handler.flush()
            handler.clear()

    # Clear operation context.
    OperationContext.get_instance().clear()
    return response


def get_custom_dimensions() -> Dict[str, str]:
    """Get custom dimensions for telemetry log."""
    operation_context = OperationContext.get_instance()
    custom_dimensions = operation_context.get_context_dict()
    custom_dimensions.update({"host_name": os.environ.get("HOSTNAME", "")})  # Docker container name.
    return custom_dimensions


def generate_error_response(e):
    if isinstance(e, JsonSerializedPromptflowException):
        error_dict = json.loads(e.message)
    else:
        error_dict = ExceptionPresenter.create(e).to_dict(include_debug_info=True)

    logger.exception("Hit exception when execute request: \n{customer_content}", extra={"customer_content": e})

    # remove traceback from response
    error_dict.pop("debugInfo", None)

    return ErrorResponse.from_error_dict(error_dict)


@app.route("/submit_single_node", methods=["POST"])
@app.route("/aml-api/v1.0/submit_single_node", methods=["POST"])
def submit_single_node():
    """Process a single node request in the runtime."""
    runtime: PromptFlowRuntime = PromptFlowRuntime.get_instance()
    req = SingleNodeRequestV2.deserialize(request.get_json())
    req_id = request.headers.get("x-ms-client-request-id")
    OperationContext.get_instance().run_mode = RunMode.SingleNode.name
    with get_log_context_from_v2_request(req):
        # Please do not change it, it is used to generate dashboard.
        logger.info(
            "[%s] Receiving v2 single node request %s: {customer_content}",
            req.flow_run_id,
            req_id,
            extra={"customer_content": req.desensitize_to_json()},
        )

        try:
            result = runtime.execute_flow(req, execute_node_request)
            logger.info("[%s] End processing single node", req.flow_run_id)

            return generate_response_from_run_result(result)
        except Exception as ex:
            _log_submit_request_exception(ex)
            raise ex


@app.route("/submit_flow", methods=["POST"])
@app.route("/aml-api/v1.0/submit_flow", methods=["POST"])
def submit_flow():
    runtime: PromptFlowRuntime = PromptFlowRuntime.get_instance()
    req = FlowRequestV2.deserialize(request.get_json())
    req_id = request.headers.get("x-ms-client-request-id")
    OperationContext.get_instance().run_mode = RunMode.Test.name
    with get_log_context_from_v2_request(req):
        # Please do not change it, it is used to generate dashboard.
        logger.info(
            "[%s] Receiving v2 flow request %s: {customer_content}",
            req.flow_run_id,
            req_id,
            extra={"customer_content": req.desensitize_to_json()},
        )

        try:
            result = runtime.execute_flow(req, execute_flow_request)
            logger.info("[%s] End processing flow v2", req.flow_run_id)

            return generate_response_from_run_result(result)
        except Exception as ex:
            _log_submit_request_exception(ex)
            raise ex


@app.route("/submit_bulk_run", methods=["POST"])
@app.route("/aml-api/v1.0/submit_bulk_run", methods=["POST"])
def submit_bulk_run():
    runtime: PromptFlowRuntime = PromptFlowRuntime.get_instance()
    OperationContext.get_instance().run_mode = RunMode.Batch.name
    payload = request.get_json()
    try:
        req = BulkRunRequestV2.deserialize(payload)
        req_id = request.headers.get("x-ms-client-request-id")
        with get_log_context_from_v2_request(req):
            # Please do not change it, it is used to generate dashboard.
            logger.info(
                "[%s] Receiving v2 bulk run request %s: {customer_content}",
                req.flow_run_id,
                req_id,
                extra={"customer_content": req.desensitize_to_json()},
            )
            mark_run_as_preparing_in_runhistory(runtime.config, req.flow_run_id)
            try:
                result = runtime.execute_flow(req, execute_bulk_run_request)
                logger.info("[%s] End processing bulk run", req.flow_run_id)
                return generate_response_from_run_result(result)
            except Exception as ex:
                _log_submit_request_exception(ex)
                raise ex
    except Exception as ex:
        runtime.mark_flow_runs_v2_as_failed(req, payload, ex)
        raise


def generate_response_from_run_result(result: dict):
    error_response: ErrorResponse = RunResultParser(result).get_error_response()
    if error_response:
        d = error_response.to_dict()
        result["errorResponse"] = d
        _log_submit_request_error_response(error_response)

        stack_trace = generate_safe_error_stacktrace(d)
        system_logger.warning(f"Log run error stack trace: \n{stack_trace}")

    resp = jsonify(result)

    return resp


@app.route("/score", methods=["POST"])
@app.route("/submit", methods=["POST"])
@app.route("/aml-api/v1.0/score", methods=["POST"])
@app.route("/aml-api/v1.0/submit", methods=["POST"])
def submit():
    """process a flow request in the runtime."""
    result = {}
    payload = request.get_json()
    req_id = request.headers.get("x-ms-client-request-id")
    if not req_id:
        req_id = request.headers.get("x-request-id")
    runtime: PromptFlowRuntime = PromptFlowRuntime.get_instance()
    flow_request = None
    try:
        flow_request = SubmitFlowRequest.deserialize(payload)
        if flow_request.run_mode is not None:
            OperationContext.get_instance().run_mode = flow_request.run_mode.get_executor_run_mode().name
        with get_log_context(flow_request), setup_contextvar(active_flow_request_context, flow_request):
            # Please do not change it, it is used to generate dashboard.
            logger.info(
                "[%s] Receiving submit flow request %s: {customer_content}",
                flow_request.flow_run_id,
                req_id,
                extra={"customer_content": SubmitFlowRequest.desensitize_to_json(flow_request)},
            )
            try:
                result = runtime.execute(flow_request)
                logger.info("[%s] End processing flow", flow_request.flow_run_id)
                # diagnostic: dump the response to a local file
                if runtime.config.execution.debug:
                    with open("output.json", "w", encoding="utf-8") as file:
                        json.dump(result, file, indent=2)

                return generate_response_from_run_result(result)
            except Exception as ex:
                _log_submit_request_exception(ex)
                raise ex
    except Exception as ex:
        runtime.mark_flow_runs_as_failed(flow_request, payload, ex)
        raise ex


@app.route("/aml-api/v1.0/package_tools")
@app.route("/package_tools")
def package_tools():
    import imp

    import pkg_resources

    imp.reload(pkg_resources)
    return jsonify(collect_package_tools())


@app.route("/aml-api/v1.0/meta", methods=["POST"])
@app.route("/meta", methods=["POST"])
def meta():
    # Get parameters and payload
    tool_type = request.args.get("tool_type", type=str)
    name = request.args.get("name", type=str)
    payload = request.get_data(as_text=True)
    logger.info(
        "Receiving meta request: tool_type=%s payload={customer_content}",
        tool_type,
        extra={"customer_content": payload},
    )

    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    exception_queue = multiprocessing.Queue()
    p = multiprocessing.Process(
        target=generate_meta_multiprocessing, args=(payload, name, tool_type, return_dict, exception_queue)
    )
    p.start()
    p.join()
    # when p is killed by signal, exitcode will be negative without exception
    if p.exitcode and p.exitcode > 0:
        exception = None
        try:
            exception = exception_queue.get(timeout=SYNC_REQUEST_TIMEOUT_THRESHOLD)
        except Exception:
            pass
        # JsonSerializedPromptflowException will be raised here
        # no need to change to PromptflowException since it will be handled in app.handle_exception
        # we can unify the exception when we decide to expose executor.execute as an public API
        if exception is not None:
            raise exception
    result = return_dict.get("result", {})

    logger.info("Result: {customer_content}", extra={"customer_content": str(result)})
    logger.info("Child process finished!")

    resp = jsonify(result)

    return resp


# S2S calls for CI need prefix "/aml-api/v1.0"
@app.route("/aml-api/v1.0/meta-v2/", methods=["POST"])
@app.route("/meta-v2", methods=["POST"])
def meta_v2():
    # Get parameters and payload
    logger.info("Receiving v2 meta request: payload = {customer_content}", extra={"customer_content": request.json})
    data = MetaV2Request.deserialize(request.json)
    runtime: PromptFlowRuntime = PromptFlowRuntime.get_instance()
    if data.flow_source_type == FlowSourceType.AzureFileShare:
        runtime_dir = fill_working_dir(
            runtime.config.deployment.compute_type, data.flow_source_info, "meta_%s" % uuid.uuid4()
        )
    elif data.flow_source_type == FlowSourceType.DataUri:
        runtime_dir = Path("requests", "meta_%s" % uuid.uuid4()).resolve()

        logger.info(
            "Preparing flow directory for dataUri: {customer_content}",
            extra={"customer_content": data.flow_source_info.data_uri},
        )
        prepare_blob_directory(data.flow_source_info.data_uri, runtime_dir, runtime_config=runtime.config)
    else:
        raise InvalidFlowSourceType(
            message_format="Invalid flow_source_type value for MetaV2Request: {flow_source_type}",
            flow_source_type=data.flow_source_type,
        )
    logger.info("Generate meta_v2 in runtime_dir {customer_content}", extra={"customer_content": runtime_dir})
    manager = multiprocessing.Manager()
    tool_dict = manager.dict()
    exception_dict = manager.dict()
    custom_dimensions = get_custom_dimensions()
    p = multiprocessing.Process(
        target=generate_metas_from_files, args=(data.tools, runtime_dir, tool_dict, exception_dict, custom_dimensions)
    )
    p.start()
    p.join(timeout=SYNC_REQUEST_TIMEOUT_THRESHOLD)
    if p.is_alive():
        logger.info(f"Stop generating meta for exceeding {SYNC_REQUEST_TIMEOUT_THRESHOLD} seconds.")
        p.terminate()
        p.join()

    resp_tools = {source: tool for source, tool in tool_dict.items()}
    # exception_dict was created by manager.dict(), so convert to a normal dict here.
    resp_errors = {source: exception for source, exception in exception_dict.items()}
    # For not processed tools, treat as timeout error.
    for source in data.tools.keys():
        if source not in resp_tools and source not in resp_errors:
            resp_errors[source] = generate_error_response(
                GenerateMetaTimeout(message_format="Generate meta timeout for source '{source}'.", source=source)
            ).to_dict()
    resp = {"tools": resp_tools, "errors": resp_errors}
    return jsonify(resp)


def generate_tool_meta_dict_by_file_allow_non_py(source, tool_type: str = "python"):
    tool_type = ToolType(tool_type)
    if tool_type == ToolType.PYTHON and not source.endswith(".py"):
        # For non-python file, we may rename it and try,
        # this is because UX will prepare another temp file without .py suffix.
        updated_source = source + ".tmp.py"
        os.rename(source, updated_source)
        return generate_tool_meta_dict_by_file(updated_source, tool_type)
    return generate_tool_meta_dict_by_file(source, tool_type)


def generate_metas_from_files(tools, runtime_dir, tool_dict, exception_dict, custom_dimensions):
    # Reinitialize logger in child process.
    with reset_and_close_logger(), set_custom_dimensions_to_logger(logger, custom_dimensions), _change_working_dir(
        runtime_dir
    ), inject_sys_path(runtime_dir):
        for source, config in tools.items():
            try:
                if "tool_type" not in config:
                    raise NoToolTypeDefined(
                        message_format="Tool type not defined for source '{source}'.", source=source
                    )
                tool_type = config.get("tool_type", ToolType.PYTHON)
                tool_dict[source] = generate_tool_meta_dict_by_file_allow_non_py(source, tool_type)
            except Exception as e:
                exception_dict[source] = generate_error_response(e).to_dict()


@app.route("/aml-api/v1.0/health", methods=["GET"])
@app.route("/health", methods=["GET"])
def health():
    """Check if the runtime is alive."""
    return {"status": "Healthy", "version": VERSION}


@app.route("/aml-api/v1.0/version", methods=["GET"])
@app.route("/version", methods=["GET"])
def version():
    """Check the runtime's version."""
    build_info = os.environ.get("BUILD_INFO", "")
    try:
        build_info_dict = json.loads(build_info)
        version = build_info_dict["build_number"]
    except Exception:
        version = VERSION
    logger.info(f"Build info: {build_info}. Version: {version}")
    return {"status": "Healthy", "build_info": build_info, "version": version}


def generate_meta_multiprocessing(content, name, tool_type, return_dict, exception_queue):
    """Generate meta data unbder isolated process.
    Note: do not change order of params since it will be used in multiprocessing executor.
    """
    with multi_processing_exception_wrapper(exception_queue):
        if tool_type == ToolType.LLM:
            result = generate_prompt_meta(name, content)
        elif tool_type == ToolType.PROMPT:
            result = generate_prompt_meta(name, content, prompt_only=True)
        else:
            result = generate_python_meta(name, content)
        return_dict["result"] = result


def create_app(config="prt.yaml", args=None):
    """Create a flask app."""
    config = Path(config).absolute()
    logger.info("Init runtime with config file in create_app: %s", config)
    config = load_runtime_config(config, args=args)
    PromptFlowRuntime.init(config)
    logger.info("Finished init runtime with config file in create_app.")
    PromptFlowRuntime.get_instance().init_storage()
    logger.info("Finished init storage in create_app.")
    return app


def _log_submit_request_exception(ex: Exception):
    resp: ErrorResponse = generate_error_response(ex)
    _log_submit_request_error_response(resp)


def _log_submit_request_error_response(resp: ErrorResponse):
    """Please do not change the texts, because they are used to generate dashboard."""
    logger.error(
        (
            "Submit flow request failed "
            f"Code: {resp.response_code} "
            f"InnerException type: {resp.innermost_error_code} "
            f"Exception type hierarchy: {resp.error_code_hierarchy}"
        )
    )


if __name__ == "__main__":
    PromptFlowRuntime.get_instance().init_logger()
    app.run()
