from pncp_analysis.pncp_client import NonJsonResponseError, ensure_json_payload
from pncp_analysis.utils import normalize_text, parse_control_number


def test_parse_control_number() -> None:
    parsed = parse_control_number("46395000000139-1-000007/2026")

    assert parsed.cnpj == "46395000000139"
    assert parsed.control_type == 1
    assert parsed.sequence == 7
    assert parsed.year == 2026


def test_normalize_text_removes_accents_and_collapses_spaces() -> None:
    assert normalize_text("  Câmara  Municipal de São Paulo ") == "CAMARA MUNICIPAL DE SAO PAULO"


def test_ensure_json_payload_rejects_html_response() -> None:
    try:
        ensure_json_payload("text/html", b"<html>Request Rejected</html>")
    except NonJsonResponseError as exc:
        assert "Expected JSON" in str(exc)
    else:
        raise AssertionError("Expected NonJsonResponseError")
