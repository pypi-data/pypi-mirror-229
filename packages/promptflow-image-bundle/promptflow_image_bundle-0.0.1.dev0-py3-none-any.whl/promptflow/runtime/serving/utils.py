import time
from promptflow.runtime.serving.metrics import ResponseType


def on_stream_start(metric_recorder, flow_id: str, start_time: float):
    def record_stream_start_metrics():
        if metric_recorder:
            duration = get_cost_up_to_now(start_time)
            metric_recorder.record_flow_latency(flow_id, 200, True, ResponseType.FirstByte.value, duration)

    return record_stream_start_metrics


def on_stream_end(metric_recorder, flow_id: str, start_time: float):
    def record_stream_end_metrics(streaming_resp_duration: float):
        if metric_recorder:
            duration = get_cost_up_to_now(start_time)
            metric_recorder.record_flow_latency(flow_id, 200, True, ResponseType.LastByte.value, duration)
            metric_recorder.record_flow_streaming_response_duration(flow_id, streaming_resp_duration)

    return record_stream_end_metrics


def get_cost_up_to_now(start_time: float):
    return (time.time() - start_time) * 1000


def enable_monitoring(func):
    func._enable_monitoring = True
    return func
