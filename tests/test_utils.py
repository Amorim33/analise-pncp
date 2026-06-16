from pncp_analysis.pncp_client import NonJsonResponseError, ensure_json_payload
from pncp_analysis.utils import (
    format_display_date,
    format_display_date_range,
    markdown_table,
    normalize_text,
    parse_control_number,
)


def test_parse_control_number() -> None:
    parsed = parse_control_number("46395000000139-1-000007/2026")

    assert parsed.cnpj == "46395000000139"
    assert parsed.control_type == 1
    assert parsed.sequence == 7
    assert parsed.year == 2026


def test_normalize_text_removes_accents_and_collapses_spaces() -> None:
    assert normalize_text("  Câmara  Municipal de São Paulo ") == "CAMARA MUNICIPAL DE SAO PAULO"


def test_format_display_date_accepts_iso_and_pncp_timestamp() -> None:
    assert format_display_date("2025-06-15") == "15/06/2025"
    assert format_display_date("2026-06-15T22:33:51") == "15/06/2026"
    assert format_display_date("20260615") == "15/06/2026"
    assert (
        format_display_date_range("2025-06-15", "2026-06-15")
        == "15/06/2025 a 15/06/2026"
    )


def test_ensure_json_payload_rejects_html_response() -> None:
    try:
        ensure_json_payload("text/html", b"<html>Request Rejected</html>")
    except NonJsonResponseError as exc:
        assert "Expected JSON" in str(exc)
    else:
        raise AssertionError("Expected NonJsonResponseError")


def test_markdown_table_escapes_pipes_and_newlines() -> None:
    table = markdown_table(["A|B"], [["linha 1\nlinha 2", "x|y"]])

    assert "A\\|B" in table
    assert "linha 1 linha 2" in table
    assert "x\\|y" in table
