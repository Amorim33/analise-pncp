from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


class NonJsonResponseError(RuntimeError):
    """Raised when the PNCP service returns HTML or another non-JSON payload."""


@dataclass(frozen=True)
class ApiFailure:
    url: str
    reason: str


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
                    self.failures.append(
                        ApiFailure(
                            url=path,
                            reason=(
                                f"Stopped pagination at page {page}; "
                                f"kept {len(records)} records already collected."
                            ),
                        )
                    )
                    break
                raise

            if isinstance(payload, list):
                records.extend(item for item in payload if isinstance(item, dict))
                break

            if not isinstance(payload, dict):
                break

            data = payload.get("data", [])
            if isinstance(data, list):
                records.extend(item for item in data if isinstance(item, dict))
            total_pages = int(payload.get("totalPaginas") or 1)

            if limit is not None and len(records) >= limit:
                return records[:limit]

            page += 1
            if max_pages is not None and page > max_pages:
                break
            if page <= total_pages:
                time.sleep(self.delay_seconds)

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
                try:
                    with urllib.request.urlopen(request, timeout=45) as response:
                        status = int(response.status)
                        body = response.read()
                        if status in empty_on_codes:
                            return []
                        return ensure_json_payload(response.headers.get("content-type", ""), body)
                except urllib.error.HTTPError as exc:
                    if exc.code in empty_on_codes:
                        return []
                    body = exc.read()
                    content_type = exc.headers.get("content-type", "")
                    last_error = RuntimeError(
                        f"HTTP {exc.code}; content-type={content_type}; body={body[:160]!r}"
                    )
                except Exception as exc:  # noqa: BLE001 - collect API boundary failures explicitly.
                    last_error = exc

                if attempt < self.retries:
                    time.sleep(self.delay_seconds * attempt)

            self.failures.append(ApiFailure(url=url, reason=str(last_error)))

        raise RuntimeError(f"PNCP request failed for {path}: {last_error}")
