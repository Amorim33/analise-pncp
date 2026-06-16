from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from pncp_analysis.utils import format_display_date


@dataclass(frozen=True)
class ScriptRunEvent:
    name: str
    command: str
    started_at: str
    finished_at: str
    duration_seconds: float | None
    exit_code: int | None
    note: str


@dataclass(frozen=True)
class ApiExperimentEvidence:
    collection_pages: int
    collection_records: int
    collection_request_count: int | None
    collection_successful_request_count: int | None
    collection_failed_attempt_count: int | None
    collection_avg_seconds: float | None
    collection_p95_seconds: float | None
    collection_max_seconds: float | None
    collection_request_metrics_path: str | None
    collection_errors_path: str | None
    collection_duration_seconds: float | None
    collection_event: ScriptRunEvent | None
    final_collection_event: ScriptRunEvent | None
    report_event: ScriptRunEvent | None
    fallback_event: ScriptRunEvent | None
    timeout_probe_event: ScriptRunEvent | None
    document_request_count: int | None
    document_successful_request_count: int | None
    document_failed_attempt_count: int | None
    document_avg_seconds: float | None
    document_p95_seconds: float | None
    document_max_seconds: float | None
    document_duration_seconds: float | None
    document_request_metrics_path: str | None
    document_errors_path: str | None


def build_api_experiment_evidence(
    collection_metadata: dict[str, Any],
    api_experiment: Any,
    script_execution_events: Any,
) -> ApiExperimentEvidence:
    collection_perf = dict_or_empty(collection_metadata.get("api_performance"))
    document_perf = {}
    document_duration = None
    document_request_metrics_path = None
    document_errors_path = None
    if isinstance(api_experiment, dict):
        document_perf = dict_or_empty(api_experiment.get("document_api_performance"))
        document_duration = optional_float(api_experiment.get("duration_seconds"))
        document_request_metrics_path = optional_str(
            api_experiment.get("document_request_metrics_path")
        )
        document_errors_path = optional_str(api_experiment.get("document_errors_path"))

    return ApiExperimentEvidence(
        collection_pages=sum_source_int(collection_metadata, "pages_collected"),
        collection_records=sum_source_int(collection_metadata, "records"),
        collection_request_count=optional_int(collection_perf.get("request_count")),
        collection_successful_request_count=optional_int(
            collection_perf.get("successful_request_count")
        ),
        collection_failed_attempt_count=optional_int(collection_perf.get("failed_attempt_count")),
        collection_avg_seconds=optional_float(
            collection_perf.get("average_success_response_seconds")
        ),
        collection_p95_seconds=optional_float(collection_perf.get("p95_success_response_seconds")),
        collection_max_seconds=optional_float(collection_perf.get("max_success_response_seconds")),
        collection_request_metrics_path=optional_str(
            collection_metadata.get("request_metrics_path")
        ),
        collection_errors_path=optional_str(collection_metadata.get("errors_path")),
        collection_duration_seconds=duration_for_event(
            script_execution_events,
            "main_successful_collection",
        )
        or optional_float(collection_metadata.get("duration_seconds")),
        collection_event=event_by_name(script_execution_events, "main_successful_collection"),
        final_collection_event=event_by_name(script_execution_events, "final_snapshot_collection"),
        report_event=event_by_name(script_execution_events, "final_report_generation"),
        fallback_event=event_by_name(script_execution_events, "fallback_run_all"),
        timeout_probe_event=event_by_name(script_execution_events, "pagination_timeout_probe"),
        document_request_count=optional_int(document_perf.get("request_count")),
        document_successful_request_count=optional_int(
            document_perf.get("successful_request_count")
        ),
        document_failed_attempt_count=optional_int(document_perf.get("failed_attempt_count")),
        document_avg_seconds=optional_float(
            document_perf.get("average_success_response_seconds")
        ),
        document_p95_seconds=optional_float(document_perf.get("p95_success_response_seconds")),
        document_max_seconds=optional_float(document_perf.get("max_success_response_seconds")),
        document_duration_seconds=document_duration,
        document_request_metrics_path=document_request_metrics_path,
        document_errors_path=document_errors_path,
    )


def estimated_total_seconds(evidence: ApiExperimentEvidence) -> float | None:
    parts = [
        evidence.collection_duration_seconds,
        evidence.document_duration_seconds,
        evidence.report_event.duration_seconds if evidence.report_event else None,
    ]
    values = [value for value in parts if value is not None]
    if not values:
        return None
    return sum(values)


def format_optional_int(value: int | None) -> str:
    return "n/a" if value is None else str(value)


def format_local_datetime(value: str) -> str:
    if len(value) < 10:
        return value or "não registrado"
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return format_display_date(value[:10])
    local = parsed.astimezone(timezone(timedelta(hours=-3)))
    return local.strftime("%d/%m/%Y %H:%M")


def dict_or_empty(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def event_by_name(script_execution_events: Any, name: str) -> ScriptRunEvent | None:
    events = dict_or_empty(script_execution_events).get("events")
    if not isinstance(events, list):
        return None
    for event in events:
        if isinstance(event, dict) and event.get("name") == name:
            return ScriptRunEvent(
                name=str(event.get("name") or ""),
                command=str(event.get("command") or ""),
                started_at=str(event.get("started_at") or ""),
                finished_at=str(event.get("finished_at") or ""),
                duration_seconds=optional_float(event.get("duration_seconds")),
                exit_code=optional_int(event.get("exit_code")),
                note=str(event.get("note") or ""),
            )
    return None


def duration_for_event(script_execution_events: Any, name: str) -> float | None:
    event = event_by_name(script_execution_events, name)
    return event.duration_seconds if event else None


def sum_source_int(collection_metadata: dict[str, Any], key: str) -> int:
    sources = collection_metadata.get("sources")
    if not isinstance(sources, list):
        return 0
    total = 0
    for source in sources:
        if isinstance(source, dict):
            value = optional_int(source.get(key))
            total += value or 0
    return total


def optional_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def optional_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    return None


def optional_str(value: Any) -> str | None:
    if isinstance(value, str) and value:
        return value
    return None
