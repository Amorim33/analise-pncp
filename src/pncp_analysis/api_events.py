from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pncp_analysis.utils import format_display_date


@dataclass(frozen=True)
class ApiSessionEvents:
    event_date: str
    endpoint_path: str
    collection_attempt_failed: bool
    collection_status: str
    attempt_duration_seconds: float | None
    pipeline_duration_seconds: float | None
    request_count: int | None
    successful_request_count: int | None
    failed_attempt_count: int | None
    status_counts: dict[str, int]
    timeout_count: int
    html_response_count: int
    document_request_count: int | None
    document_successful_request_count: int | None
    document_failed_attempt_count: int | None
    document_avg_seconds: float | None
    document_max_seconds: float | None


def build_api_session_events(
    api_experiment: Any,
    pipeline_metadata: dict[str, Any],
) -> ApiSessionEvents | None:
    attempt = dict_or_empty(pipeline_metadata.get("collection_attempt"))
    if not attempt:
        return None

    attempt_perf = dict_or_empty(attempt.get("api_performance"))
    document_perf = {}
    if isinstance(api_experiment, dict):
        document_perf = dict_or_empty(api_experiment.get("document_api_performance"))

    status_counts = parse_status_counts(attempt_perf.get("status_counts"))
    failed_count = optional_int(attempt_perf.get("failed_attempt_count"))
    return ApiSessionEvents(
        event_date=event_date(attempt, pipeline_metadata),
        endpoint_path=primary_path(attempt_perf),
        collection_attempt_failed=attempt.get("status") == "failed",
        collection_status=str(pipeline_metadata.get("collection_status") or ""),
        attempt_duration_seconds=optional_float(attempt.get("duration_seconds")),
        pipeline_duration_seconds=optional_float(pipeline_metadata.get("duration_seconds")),
        request_count=optional_int(attempt_perf.get("request_count")),
        successful_request_count=optional_int(attempt_perf.get("successful_request_count")),
        failed_attempt_count=failed_count,
        status_counts=status_counts,
        timeout_count=count_timeouts(attempt_perf, status_counts, failed_count),
        html_response_count=count_html_responses(attempt_perf, status_counts),
        document_request_count=optional_int(document_perf.get("request_count")),
        document_successful_request_count=optional_int(
            document_perf.get("successful_request_count")
        ),
        document_failed_attempt_count=optional_int(document_perf.get("failed_attempt_count")),
        document_avg_seconds=optional_float(
            document_perf.get("average_success_response_seconds")
        ),
        document_max_seconds=optional_float(document_perf.get("max_success_response_seconds")),
    )


def format_status_counts_pt(status_counts: dict[str, int]) -> str:
    if not status_counts:
        return "sem codigos HTTP registrados"
    parts = []
    for status, count in sorted(status_counts.items(), key=status_sort_key):
        label = f"HTTP {status}"
        if status == "503":
            label += " (Service Unavailable)"
        noun = "resposta" if count == 1 else "respostas"
        parts.append(f"{count} {noun} {label}")
    return ", ".join(parts)


def format_optional_int(value: int | None) -> str:
    return "n/a" if value is None else str(value)


def pluralize(count: int, singular: str, plural: str) -> str:
    return f"{count} {singular if count == 1 else plural}"


def dict_or_empty(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def list_or_empty(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


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


def parse_status_counts(value: Any) -> dict[str, int]:
    if not isinstance(value, dict):
        return {}
    parsed: dict[str, int] = {}
    for raw_status, raw_count in value.items():
        count = optional_int(raw_count)
        if count is not None:
            parsed[str(raw_status)] = count
    return parsed


def count_timeouts(
    performance: dict[str, Any],
    status_counts: dict[str, int],
    failed_count: int | None,
) -> int:
    examples = list_or_empty(performance.get("failure_examples"))
    example_timeouts = sum(
        1
        for item in examples
        if isinstance(item, dict)
        and "timed out" in str(item.get("error") or "").lower()
    )
    if failed_count is None:
        return example_timeouts
    failures_without_status = max(failed_count - sum(status_counts.values()), 0)
    return max(example_timeouts, failures_without_status)


def count_html_responses(
    performance: dict[str, Any],
    status_counts: dict[str, int],
) -> int:
    examples = list_or_empty(performance.get("failure_examples"))
    html_examples = sum(
        1
        for item in examples
        if isinstance(item, dict)
        and any(
            marker in str(item.get("error") or "").lower()
            for marker in ["text/html", "<html"]
        )
    )
    if html_examples and "503" in status_counts:
        return max(html_examples, status_counts["503"])
    return html_examples


def event_date(attempt: dict[str, Any], pipeline_metadata: dict[str, Any]) -> str:
    for payload in [attempt, pipeline_metadata]:
        for key in ["started_at", "generated_at", "finished_at"]:
            value = payload.get(key)
            if isinstance(value, str) and len(value) >= 10:
                return format_display_date(value[:10])
    return "data nao registrada"


def primary_path(performance: dict[str, Any]) -> str:
    paths = performance.get("paths")
    if isinstance(paths, dict) and paths:
        return str(next(iter(paths)))
    for item in list_or_empty(performance.get("failure_examples")):
        if isinstance(item, dict) and item.get("path"):
            return str(item["path"])
    return "endpoint de coleta"


def status_sort_key(item: tuple[str, int]) -> tuple[int, str]:
    status, _count = item
    try:
        return (int(status), status)
    except ValueError:
        return (999, status)
