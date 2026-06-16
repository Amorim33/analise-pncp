import time

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
