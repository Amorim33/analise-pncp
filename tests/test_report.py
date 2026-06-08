from pncp_analysis.config import AnalysisConfig, ApiConfig, SaoPauloFilterConfig
from pncp_analysis.report import render_report


def test_render_report_contains_required_sections() -> None:
    config = AnalysisConfig(
        start_date="2026-01-01",
        end_date="2026-05-31",
        modality_id=6,
        modality_name="Pregao - Eletronico",
        sample_n=10,
        seed=20260608,
        api=ApiConfig(
            query_bases=[],
            document_bases=[],
            page_size=50,
            municipality_scan_max_pages=5,
            request_delay_seconds=0.0,
            retries=1,
        ),
        sao_paulo_filter=SaoPauloFilterConfig(include_indicators=[], exclude_indicators=[]),
        cities=[],
    )
    metrics = {
        "api_examples": [],
        "additional_findings": [],
        "city_metrics": [],
        "document_stats": [],
        "field_completeness": [],
        "sao_paulo_fragmentation_evidence": {},
        "sao_paulo_top_cnpjs": [],
        "sample_rows": [],
        "limitations": ["Limitacao de teste."],
    }

    report = render_report(config, metrics, [])

    assert "# Analise exploratoria do PNCP nas capitais do Sudeste" in report
    assert "## Metodologia" in report
    assert "## Exemplos de registros retornados pela API" in report
    assert "## Constatações adicionais" in report
    assert "## Fragmentacao de CNPJs em Sao Paulo" in report
    assert "## Documentos vinculados" in report
    assert "## Conclusao regional" in report
