import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Mapping

from promptflow._legacy.executor import FlowExecutionCoodinator
from promptflow.contracts.flow import Flow
from promptflow.contracts.run_info import FlowRunInfo
from promptflow.contracts.run_info import RunInfo as NodeRunInfo
from promptflow.executor.flow_executor import FlowExecutor
from promptflow.runtime.utils import logger
from promptflow.runtime.utils._utils import decode_dict


@dataclass
class FlowResult:
    """The result of a flow call."""

    output: Mapping[str, Any]  # The output of the line.
    run_info: FlowRunInfo  # The run info of the line.
    node_run_infos: Mapping[str, NodeRunInfo]  # The run info of the nodes in the line.


class ConnectionLoadingType(Enum):
    Workspace = "workspace"
    Environment = "environment"


class FlowInvoker:
    """The invoker of a flow."""

    def __init__(
        self,
        flow_file: Path,
        stream_required: Callable[[], bool],
        conn_loading_type: ConnectionLoadingType,
        **kwargs: Any,
    ):
        self._flow_loaded = False
        self._flow_file = flow_file
        self._coordinator: FlowExecutionCoodinator = FlowExecutionCoodinator.init_from_env()
        self._executor: FlowExecutor = None
        self._stream_required = stream_required
        self._conn_loading_type = conn_loading_type
        self._subscription_id = kwargs.get("subscription_id", None)
        self._resource_group = kwargs.get("resource_group", None)
        self._workspace_name = kwargs.get("workspace_name", None)
        try:
            self._try_load()
        except Exception as e:
            logger.warn(f"Flow invoker load flow failed: {e}")

    def load_success(self) -> bool:
        return self._flow_loaded

    def invoke(self, data, run_id=None, allow_generator_output=False) -> FlowResult:
        """Invoke the flow with the given data."""
        if not self._flow_loaded:
            self._try_load()
        result = self._executor.exec_line(data, run_id=run_id, allow_generator_output=allow_generator_output)
        return FlowResult(
            output=result.output or {},
            run_info=result.run_info,
            node_run_infos=result.node_run_infos,
        )

    @property
    def flow(self) -> Flow:
        if not self._flow_loaded:
            self._try_load()
        return self._executor._flow

    def _try_load(self):
        logger.info("Try loading connections...")
        connections = self._load_connection(self._flow_file)
        logger.info("Loading flow...")
        # TODO: change to FlowExecutor.create() once the old contract is not supported
        self._executor = self._coordinator.create_flow_executor_by_model(
            flow_file=self._flow_file, connections=connections
        )
        self._executor._raise_ex = False
        self._executor.enable_streaming_for_llm_flow(self._stream_required)
        self._flow_loaded = True
        logger.info("Flow loaded successfully.")

    def _load_connection(self, flow_file: Path):
        if self._conn_loading_type == ConnectionLoadingType.Workspace:
            logger.info("Promptflow serving runtime start getting connections from workspace...")
            connections = _prepare_workspace_connections(
                flow_file, self._subscription_id, self._resource_group, self._workspace_name
            )
        else:
            connections = _prepare_env_connections()
        logger.info(f"Promptflow serving runtime get connections successfully. keys: {connections.keys()}")
        return connections


def _prepare_workspace_connections(flow_file, subscription_id, resource_group, workspace_name):
    flow_file = Path(flow_file)
    # Resolve connection names from flow.
    logger.info("Reading flow from model ...")
    flow = Flow.from_yaml(flow_file, gen_tool=True)
    logger.info("Getting connection names for flow ...")
    connection_names = flow.get_connection_names()
    from promptflow.runtime.connections import build_connection_dict

    logger.info(f"Getting connection from workspace and build dict for flow ... connection names: {connection_names}")
    # Get workspace connection and return as a dict.
    return build_connection_dict(connection_names, subscription_id, resource_group, workspace_name)


def _prepare_env_connections():
    # TODO: support loading from environment once secret injection is ready
    # For local test app connections will be set.
    env_connections = os.getenv("PROMPTFLOW_ENCODED_CONNECTIONS", None)
    if not env_connections:
        logger.info("Promptflow serving runtime received no connections from environment!!!")
        connections = {}
    else:
        connections = decode_dict(env_connections)
    return connections
