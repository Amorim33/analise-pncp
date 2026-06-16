from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from dataclasses import dataclass
from typing import Any


class NonJsonResponseError(RuntimeError):
    """Raised when the PNCP service returns HTML or another non-JSON payload."""


RATE_LIMIT_BACKOFF_SECONDS = 60.0


@dataclass(frozen=True)
class ApiFailure:
    url: str
    reason: str


@dataclass(frozen=True)
class ApiRequestMetric:
    path: str
    url: str
    status: int | None
    duration_seconds: float
    attempt: int
    success: bool
    error: str | None


@dataclass(frozen=True)
class PaginationMetadata:
    path: str
    pages_collected: int
    total_pages: int | None
    total_records: int | None
    complete: bool
    stopped_reason: str | None


def ensure_json_payload(content_type: str, body: bytes) -> Any:
    if "json" not in content_type.lower():
        preview = body[:180].decode("utf-8", errors="replace").replace("\n", " ")
        raise NonJsonResponseError(f"Expected JSON, got {content_type}: {preview}")
    return json.loads(body.decode("utf-8"))


class PncpClient:
    def __init__(
        self,
        query_bases: list[str],
        document_bases: list[str],
        page_size: int,
        delay_seconds: float,
        retries: int,
    ) -> None:
        self.query_bases = [base.rstrip("/") for base in query_bases]
        self.document_bases = [base.rstrip("/") for base in document_bases]
        self.page_size = page_size
        self.delay_seconds = delay_seconds
        self.retries = retries
        self.failures: list[ApiFailure] = []
        self.last_pagination: PaginationMetadata | None = None
        self.request_metrics: list[ApiRequestMetric] = []

    def fetch_contratacoes(
        self,
        *,
        start_date: str,
        end_date: str,
        modality_id: int,
        cnpj: str | None = None,
        uf: str | None = None,
        ibge: str | None = None,
        limit: int | None = None,
        max_pages: int | None = None,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {
            "dataInicial": start_date,
            "dataFinal": end_date,
            "codigoModalidadeContratacao": modality_id,
        }
        if cnpj:
            params["cnpj"] = cnpj
        if uf:
            params["uf"] = uf
        if ibge:
            params["codigoMunicipioIbge"] = ibge

        return self._fetch_paginated(
            "/v1/contratacoes/publicacao",
            params=params,
            bases=self.query_bases,
            limit=limit,
            max_pages=max_pages,
        )

    def fetch_purchase_documents(
        self,
        *,
        cnpj: str,
        year: int,
        sequence: int,
    ) -> list[dict[str, Any]]:
        path = f"/v1/orgaos/{cnpj}/compras/{year}/{sequence}/arquivos"
        payload = self._request_json(
            path,
            params={"pagina": 1, "tamanhoPagina": self.page_size},
            bases=self.document_bases,
            empty_on_codes={204, 404},
        )
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        if isinstance(payload, dict):
            data = payload.get("data", [])
            if isinstance(data, list):
                return [item for item in data if isinstance(item, dict)]
        return []

    def _fetch_paginated(
        self,
        path: str,
        *,
        params: dict[str, Any],
        bases: list[str],
        limit: int | None = None,
        max_pages: int | None = None,
    ) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        page = 1
        total_pages = 1
        total_records: int | None = None
        pages_collected = 0
        stopped_reason: str | None = None

        while page <= total_pages:
            page_params = dict(params)
            page_params["pagina"] = page
            page_params["tamanhoPagina"] = self.page_size
            try:
                payload = self._request_json(
                    path,
                    params=page_params,
                    bases=bases,
                    empty_on_codes={204},
                )
            except RuntimeError:
                if records:
                    stopped_reason = (
                        f"Stopped pagination at page {page}; "
                        f"kept {len(records)} records already collected."
                    )
                    self.failures.append(
                        ApiFailure(
                            url=path,
                            reason=stopped_reason,
                        )
                    )
                    break
                raise

            if isinstance(payload, list):
                records.extend(item for item in payload if isinstance(item, dict))
                pages_collected = 1
                total_pages = 1
                total_records = len(records)
                self.last_pagination = PaginationMetadata(
                    path=path,
                    pages_collected=pages_collected,
                    total_pages=total_pages,
                    total_records=total_records,
                    complete=True,
                    stopped_reason=None,
                )
                return records

            if not isinstance(payload, dict):
                stopped_reason = "Non-object pagination payload."
                break

            data = payload.get("data", [])
            if isinstance(data, list):
                records.extend(item for item in data if isinstance(item, dict))
            pages_collected += 1
            total_pages = int(payload.get("totalPaginas") or 1)
            total_records = optional_int(payload.get("totalRegistros"))

            if limit is not None and len(records) >= limit:
                self.last_pagination = PaginationMetadata(
                    path=path,
                    pages_collected=pages_collected,
                    total_pages=total_pages,
                    total_records=total_records,
                    complete=False,
                    stopped_reason=f"Limit reached at {limit} records.",
                )
                return records[:limit]

            page += 1
            if max_pages is not None and page > max_pages and page <= total_pages:
                stopped_reason = f"Max pages reached at {max_pages} pages."
                break
            if page <= total_pages:
                time.sleep(self.delay_seconds)

        complete = stopped_reason is None and page > total_pages
        self.last_pagination = PaginationMetadata(
            path=path,
            pages_collected=pages_collected,
            total_pages=total_pages,
            total_records=total_records,
            complete=complete,
            stopped_reason=stopped_reason,
        )
        return records

    def _request_json(
        self,
        path: str,
        *,
        params: dict[str, Any],
        bases: list[str],
        empty_on_codes: set[int],
    ) -> Any:
        encoded = urllib.parse.urlencode(params)
        normalized_path = "/" + path.lstrip("/")
        last_error: Exception | None = None

        for base in bases:
            url = f"{base}{normalized_path}"
            if encoded:
                url = f"{url}?{encoded}"

            for attempt in range(1, self.retries + 1):
                request = urllib.request.Request(url, headers={"Accept": "application/json"})
                started = time.perf_counter()
                try:
                    with urllib.request.urlopen(request, timeout=45) as response:
                        status = int(response.status)
                        body = response.read()
                        if status in empty_on_codes:
                            self._record_request(
                                path=normalized_path,
                                url=url,
                                status=status,
                                started=started,
                                attempt=attempt,
                                success=True,
                                error=None,
                            )
                            return []
                        payload = ensure_json_payload(
                            response.headers.get("content-type", ""),
                            body,
                        )
                        self._record_request(
                            path=normalized_path,
                            url=url,
                            status=status,
                            started=started,
                            attempt=attempt,
                            success=True,
                            error=None,
                        )
                        return payload
                except urllib.error.HTTPError as exc:
                    if exc.code in empty_on_codes:
                        self._record_request(
                            path=normalized_path,
                            url=url,
                            status=exc.code,
                            started=started,
                            attempt=attempt,
                            success=True,
                            error=None,
                        )
                        return []
                    body = exc.read()
                    content_type = exc.headers.get("content-type", "")
                    last_error = RuntimeError(
                        f"HTTP {exc.code}; content-type={content_type}; body={body[:160]!r}"
                    )
                    self._record_request(
                        path=normalized_path,
                        url=url,
                        status=exc.code,
                        started=started,
                        attempt=attempt,
                        success=False,
                        error=str(last_error),
                    )
                    if exc.code == 429 and attempt < self.retries:
                        time.sleep(RATE_LIMIT_BACKOFF_SECONDS * attempt)
                        continue
                except Exception as exc:  # noqa: BLE001 - collect API boundary failures explicitly.
                    last_error = exc
                    self._record_request(
                        path=normalized_path,
                        url=url,
                        status=None,
                        started=started,
                        attempt=attempt,
                        success=False,
                        error=str(exc),
                    )

                if attempt < self.retries:
                    time.sleep(self.delay_seconds * attempt)

            self.failures.append(ApiFailure(url=url, reason=str(last_error)))

        raise RuntimeError(f"PNCP request failed for {path}: {last_error}")

    def _record_request(
        self,
        *,
        path: str,
        url: str,
        status: int | None,
        started: float,
        attempt: int,
        success: bool,
        error: str | None,
    ) -> None:
        self.request_metrics.append(
            ApiRequestMetric(
                path=path,
                url=url,
                status=status,
                duration_seconds=time.perf_counter() - started,
                attempt=attempt,
                success=success,
                error=error,
            )
        )

    def request_summary(self) -> dict[str, Any]:
        successes = [metric for metric in self.request_metrics if metric.success]
        failures = [metric for metric in self.request_metrics if not metric.success]
        success_durations = [metric.duration_seconds for metric in successes]
        return {
            "request_count": len(self.request_metrics),
            "successful_request_count": len(successes),
            "failed_attempt_count": len(failures),
            "average_success_response_seconds": rounded_average(success_durations),
            "max_success_response_seconds": round(max(success_durations), 3)
            if success_durations
            else None,
            "total_success_response_seconds": round(sum(success_durations), 3),
            "status_counts": {
                str(status): count
                for status, count in sorted(
                    Counter(
                        metric.status
                        for metric in self.request_metrics
                        if metric.status is not None
                    ).items()
                )
            },
            "paths": {
                path: count
                for path, count in sorted(
                    Counter(metric.path for metric in self.request_metrics).items()
                )
            },
            "failure_examples": [
                {
                    "path": metric.path,
                    "status": metric.status,
                    "attempt": metric.attempt,
                    "error": metric.error,
                }
                for metric in failures[:5]
            ],
        }


def rounded_average(values: list[float]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 3)


def optional_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
