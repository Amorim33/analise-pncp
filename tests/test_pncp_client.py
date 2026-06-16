import time
import urllib.request
from email.message import Message

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
