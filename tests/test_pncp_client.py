import time
import urllib.request
from email.message import Message

import pytest

from pncp_analysis.pncp_client import PncpClient


def test_request_summary_counts_successes_and_failures() -> None:
    client = PncpClient(
        query_bases=[],
        document_bases=[],
        page_size=50,
        delay_seconds=0,
        retries=1,
    )

    client._record_request(
        path="/v1/teste",
        url="https://example.test/v1/teste",
        status=200,
        started=time.perf_counter(),
        attempt=1,
        success=True,
        error=None,
    )
    client._record_request(
        path="/v1/teste",
        url="https://example.test/v1/teste",
        status=429,
        started=time.perf_counter(),
        attempt=1,
        success=False,
        error="HTTP 429",
    )

    summary = client.request_summary()

    assert summary["request_count"] == 2
    assert summary["successful_request_count"] == 1
    assert summary["failed_attempt_count"] == 1
    assert summary["status_counts"] == {"200": 1, "429": 1}
    assert summary["paths"] == {"/v1/teste": 2}
    assert summary["median_success_response_seconds"] is not None
    assert summary["p95_success_response_seconds"] is not None


def test_request_records_include_timing_and_error_details() -> None:
    client = PncpClient(
        query_bases=[],
        document_bases=[],
        page_size=50,
        delay_seconds=0,
        retries=1,
    )

    client._record_request(
        path="/v1/teste",
        url="https://example.test/v1/teste",
        status=503,
        started=time.perf_counter(),
        attempt=2,
        success=False,
        error="HTTP 503",
    )

    records = client.request_records(phase="collection")

    assert records == [
        {
            "phase": "collection",
            "path": "/v1/teste",
            "url": "https://example.test/v1/teste",
            "status": 503,
            "started_at": records[0]["started_at"],
            "finished_at": records[0]["finished_at"],
            "duration_seconds": records[0]["duration_seconds"],
            "attempt": 2,
            "success": False,
            "error": "HTTP 503",
        }
    ]
    assert records[0]["duration_seconds"] >= 0


def test_fetch_document_binary_accepts_non_json_payload(monkeypatch) -> None:
    client = PncpClient(
        query_bases=[],
        document_bases=[],
        page_size=50,
        delay_seconds=0,
        retries=1,
    )

    class FakeResponse:
        status = 200

        def __init__(self) -> None:
            self.headers = Message()
            self.headers["content-type"] = "application/octet-stream"
            self.headers["content-disposition"] = 'attachment; filename="edital.zip"'

        def __enter__(self) -> "FakeResponse":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def read(self) -> bytes:
            return b"not-json"

    def fake_urlopen(request: urllib.request.Request, timeout: int) -> FakeResponse:
        assert timeout == 60
        assert request.full_url == "https://example.test/doc"
        return FakeResponse()

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    binary = client.fetch_document_binary(url="https://example.test/doc")

    assert binary.body == b"not-json"
    assert binary.content_type == "application/octet-stream"
    assert binary.filename == "edital.zip"
    assert client.request_summary()["successful_request_count"] == 1


def test_fetch_document_binary_rejects_non_http_url() -> None:
    client = PncpClient(
        query_bases=[],
        document_bases=[],
        page_size=50,
        delay_seconds=0,
        retries=1,
    )

    with pytest.raises(ValueError, match="Unsupported document URL"):
        client.fetch_document_binary(url="file:///etc/passwd")


def test_fetch_document_binary_sanitizes_header_filename(monkeypatch) -> None:
    client = PncpClient(
        query_bases=[],
        document_bases=[],
        page_size=50,
        delay_seconds=0,
        retries=1,
    )

    class FakeResponse:
        status = 200

        def __init__(self) -> None:
            self.headers = Message()
            self.headers["content-type"] = "application/pdf"
            self.headers["content-disposition"] = 'attachment; filename="../edital.pdf"'

        def __enter__(self) -> "FakeResponse":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def read(self) -> bytes:
            return b"pdf"

    def fake_urlopen(request: urllib.request.Request, timeout: int) -> FakeResponse:
        return FakeResponse()

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    binary = client.fetch_document_binary(url="https://example.test/doc")

    assert binary.filename == "edital.pdf"


def test_fetch_paginated_applies_limit_to_list_payload(monkeypatch) -> None:
    client = PncpClient(
        query_bases=["https://example.test"],
        document_bases=[],
        page_size=50,
        delay_seconds=0,
        retries=1,
    )

    def fake_request_json(
        path: str,
        *,
        params: dict[str, object],
        bases: list[str],
        empty_on_codes: set[int],
    ) -> list[dict[str, int]]:
        return [{"id": 1}, {"id": 2}]

    monkeypatch.setattr(client, "_request_json", fake_request_json)

    records = client._fetch_paginated(
        "/v1/teste",
        params={},
        bases=["https://example.test"],
        limit=1,
    )

    assert records == [{"id": 1}]


def test_fetch_paginated_collects_dict_pages(monkeypatch) -> None:
    client = PncpClient(
        query_bases=["https://example.test"],
        document_bases=[],
        page_size=50,
        delay_seconds=0,
        retries=1,
    )
    payloads = [
        {"data": [{"id": 1}], "totalPaginas": 2, "totalRegistros": 2},
        {"data": [{"id": 2}], "totalPaginas": 2, "totalRegistros": 2},
    ]

    def fake_request_json(
        path: str,
        *,
        params: dict[str, object],
        bases: list[str],
        empty_on_codes: set[int],
    ) -> dict[str, object]:
        return payloads[int(params["pagina"]) - 1]

    monkeypatch.setattr(client, "_request_json", fake_request_json)

    records = client._fetch_paginated(
        "/v1/teste",
        params={},
        bases=["https://example.test"],
    )

    assert records == [{"id": 1}, {"id": 2}]
    assert client.last_pagination is not None
    assert client.last_pagination.complete
