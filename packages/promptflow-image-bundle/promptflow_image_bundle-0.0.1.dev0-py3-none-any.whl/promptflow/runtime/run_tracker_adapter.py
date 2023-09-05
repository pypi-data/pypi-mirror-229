import json
from typing import List, Optional

from promptflow._internal import ErrorResponse, RootErrorCode, RunTracker, add_metric_logger, logger
from promptflow.contracts.run_info import FlowRunInfo, RunInfo
from promptflow.contracts.run_mode import RunMode
from promptflow.exceptions import ErrorTarget, ValidationException
from promptflow.runtime.constants import TOTAL_CHILD_RUNS_KEY, PromptflowEdition


class RunTrackerAdapter:
    """RunTrackerAdapter wraps core RunTracker and AzureMLRunStorageV2
    to update flow run status and metrics to run history.
    It's to replace the LegacyRunTracker.
    """

    def __init__(self, run_tracker: RunTracker, run_mode: RunMode):
        self._run_tracker = run_tracker
        self._storage = run_tracker._storage
        self._run_mode = run_mode
        # register metric logger
        add_metric_logger(self.log_metric)

    def _is_bulk_test(self):
        return self._run_mode == RunMode.Batch

    def _should_upload_metrics(self):
        return self._run_mode == RunMode.Batch

    def _should_update_run_history(self):
        return self._run_mode == RunMode.Batch and self._storage._edition == PromptflowEdition.ENTERPRISE

    def start_root_flow_run(self, flow_id, root_run_id):
        root_run_info = self._run_tracker.start_flow_run(
            flow_id=flow_id,
            run_id=root_run_id,
            root_run_id=root_run_id,
            parent_run_id="",
        )

        if self._should_upload_metrics():
            root_run_info.upload_metrics = True

        if self._should_update_run_history():
            self._storage._start_aml_root_run(run_id=root_run_id)

        return root_run_info

    def end_root_flow_run(
        self,
        run_id: str,
        *,
        result: Optional[dict] = None,
        ex: Optional[Exception] = None,
        traces: Optional[List] = None,
        update_at_last: Optional[bool] = None,
    ):
        root_run_info = self._run_tracker.end_run(run_id=run_id, result=result, ex=ex, traces=traces)

        if update_at_last is True and isinstance(root_run_info, FlowRunInfo):
            self.update_flow_run_info(root_run_info)

    def update_flow_run_info(self, run_info: FlowRunInfo):
        self._storage.update_flow_run_info(run_info)

    def persist_status_summary(self, status_summary: dict, run_id: str):
        self._storage.persist_status_summary(status_summary, run_id)

    def root_run_postprocess(self, run_info: FlowRunInfo):
        # For root level flow run, it is actually the parent of the flow runs of all lines of data,
        # it needs to collect all metrics from all lines.
        self._set_flow_metrics(run_info.run_id)
        # Root run should also aggregate child run errors to root run's error
        self._aggregate_child_run_errors(run_info)

    def _set_flow_metrics(self, run_id):
        run_info = self._run_tracker.ensure_run_info(run_id)
        if not isinstance(run_info, FlowRunInfo):
            return

        node_run_infos = self._run_tracker.collect_node_runs(run_id)
        run_info.system_metrics = run_info.system_metrics or {}
        run_info.system_metrics.update(
            self._run_tracker.collect_metrics(node_run_infos, RunTracker.OPENAI_AGGREGATE_METRICS)
        )

        child_runs_count = len(
            [run_info for run_info in self._run_tracker.flow_run_list if run_info.parent_run_id == run_id]
        )
        run_info.system_metrics[TOTAL_CHILD_RUNS_KEY] = child_runs_count

    def _aggregate_child_run_errors(self, root_run_info: FlowRunInfo):
        """Aggregate child run errors to root run's error.

        (Example)
            Base flow run (variant_0)
                Child run 0 (line data 0) -> Succeeded
                Child run 1 (line data 1) -> Failed by UserError/SubUserError
                Child run 2 (line data 2) -> Failed by SystemError/SubSystemError

            Root run's error messageFormat would be a json string of a dict:
            {
                "totalChildRuns": 3,
                "userErrorChildRuns": 1,
                "systemErrorChildRuns": 1,
                "errorDetails": [
                    {
                        "code": "UserError/SubUserError",
                        "messageFormat": "Sample user error message",
                        "count": 1
                    },
                    {
                        "code": "SystemError/SubSystemError",
                        "messageFormat": "Sample system error message",
                        "count": 1
                    }
                ]
            }

            So the full error response of this root run would be like:
            {
                "error": {
                    "code": "SystemError/SubSystemError",
                    "message": "I don't like banana!",
                    "messageFormat": '{"totalChildRuns": 3, "userErrorChildRuns": 1, "systemErrorChildRuns": 1, "errorDetails": [{"code": "UserError/SubUserError", "message": "Sample user error message", "count": 1}, {"code": "SystemError/SubSystemError", "message": "Sample user error message", "count": 1}]}',                     "message": '{"totalChildRuns": 3, "userErrorChildRuns": 1, "systemErrorChildRuns": 1, "errorDetails": [{"code": "UserError/SubUserError", "message": "Sample user error message", "count": 1}, {"code": "SystemError/SubSystemError", "message": "Sample user error message", "count": 1}]}',   # noqa: E501
                }
                "componentName": "promptflow/{runtime_version}"
            }

            Note that the message_format is the message_format of the first system error child run, if no such child run it
            is the error message_format of the first user error child run.

            messageFormat is a json string of aggregated child run error info.
        """
        # get all child runs info
        child_runs = [
            run_info for run_info in self._run_tracker.flow_run_list if run_info.parent_run_id == root_run_info.run_id
        ]
        if not child_runs:
            return
        child_runs = sorted(child_runs, key=lambda run_info: run_info.run_id)

        # calculate the number of user error and system error child runs
        user_error_child_runs = [
            run_info for run_info in child_runs if run_info.error and run_info.error["code"] == RootErrorCode.USER_ERROR
        ]
        system_error_child_runs = [
            run_info
            for run_info in child_runs
            if run_info.error and run_info.error["code"] == RootErrorCode.SYSTEM_ERROR
        ]
        error_details = {}

        # set root run error dict as first system or user error child run's error dict
        if user_error_child_runs:
            root_run_info.error = user_error_child_runs[0].error
        if system_error_child_runs:
            root_run_info.error = system_error_child_runs[0].error

        # aggregate child runs' errors, update root run error message
        for run_info in child_runs:
            error = run_info.error
            if error is None:
                continue

            # use error code and error message as key to aggregate
            error_key = error["code"] + error.get("messageFormat", "")
            if error_key not in error_details:
                error_details[error_key] = {
                    "code": ErrorResponse(error).error_code_hierarchy,
                    "messageFormat": error.get("messageFormat", ""),
                    "count": 1,
                }
            else:
                error_details[error_key]["count"] += 1

        # update root run error message with aggregated error details
        if error_details:
            # there is a hard limitation for writing run history error message which is 3000 characters
            # so we use "messageFormat" to store the full error message, the limitation for "messageFormat"
            # is between 1.6 million and 3.2 million characters
            root_run_info.error["messageFormat"] = json.dumps(
                {
                    "totalChildRuns": len(child_runs),
                    "userErrorChildRuns": len(user_error_child_runs),
                    "systemErrorChildRuns": len(system_error_child_runs),
                    "errorDetails": self._validate_error_details(list(error_details.values())),
                }
            )

    def _validate_error_details(self, error_list):
        """
        Make sure error details json string size is less than 1.6 million characters. Truncate the error detail
        to not exceed the limit if needed.
        """
        MAX_JSON_STRING_SIZE = 1600000
        while len(json.dumps(error_list)) > MAX_JSON_STRING_SIZE:
            old_length = len(error_list)
            new_length = old_length // 2
            error_list = error_list[:new_length]
            logger.warning(
                f"Error details json string size exceeds limit {MAX_JSON_STRING_SIZE!r}, "
                f"truncated error details item count from {old_length!r} to {new_length!r}."
            )

        return error_list

    def log_metric(self, key, value, variant_id=None):
        run_tracker_active = self._run_tracker.active()
        run_id = self._run_tracker.get_current_run_in_context()
        if not run_tracker_active or not run_id:
            logger.warning(f"Cannot log metric {key}={value} because no run is active")
            return
        run_info = self._run_tracker.get_run(run_id)
        if not isinstance(run_info, RunInfo):
            logger.warning(f"Cannot log metric {key}={value} because run {run_id} is not a node run")
            return
        flow_run_info = self._run_tracker.get_run(run_info.parent_run_id)
        if not isinstance(flow_run_info, FlowRunInfo):
            parent_run_id = run_info.parent_run_id
            logger.warning(
                f"Cannot log metric {key}={value} because {run_id}'s parent {parent_run_id} is not a flow run"
            )
            return
        if flow_run_info.root_run_id != flow_run_info.run_id:
            message = (
                f"Only aggregation node can log metrics. Please make sure '{run_info.node}' is an aggregation node."
            )
            raise NodeTypeNotSupportedForLoggingMetric(message=message, target=ErrorTarget.TOOL)
        if variant_id and not isinstance(variant_id, str):
            message = f"variant_id must be a string, got {variant_id} of type {type(variant_id)}"
            raise VariantIdTypeError(message=message, target=ErrorTarget.TOOL)
        try:
            value = float(value)
        except (TypeError, ValueError) as e:
            logger.warning(
                f"Cannot log metric because the value is not a number. Metric {key}={value} of type {type(value)}"
            )
            logger.warning(str(e))
            #  Currently this is just for backward compatibility. We should remove this in the future.
            return

        # Add metrics to run info
        if flow_run_info.metrics is None:
            flow_run_info.metrics = {}
        if key not in flow_run_info.metrics:
            flow_run_info.metrics[key] = []
        item = {"value": value}
        if variant_id is not None:
            item["variant_id"] = variant_id
        flow_run_info.metrics[key].append(item)


class NodeTypeNotSupportedForLoggingMetric(ValidationException):
    pass


class VariantIdTypeError(ValidationException):
    pass
