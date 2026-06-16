from pncp_analysis.config import AnalysisConfig, ApiConfig, SaoPauloFilterConfig
from pncp_analysis.report import render_report


def test_render_report_contains_required_sections() -> None:
    config = AnalysisConfig(
        start_date="2025-06-15",
        end_date="2026-06-15",
        modality_id=6,
        modality_name="Pregao - Eletronico",
        sample_strategy="all",
        sample_n=None,
        document_sample_n=100,
        seed=20260608,
        api=ApiConfig(
            query_bases=[],
            document_bases=[],
            page_size=50,
            municipality_scan_max_pages=None,
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
        "sample": {"strategy": "all", "n": None, "seed": 20260608, "document_n": 100},
        "document_sample": {"counts_by_city": {}},
    }

    report = render_report(config, metrics, [])

    assert "# Analise exploratoria do PNCP nas capitais do Sudeste" in report
    assert "## Metodologia" in report
    assert "## Exemplos de registros retornados pela API" in report
    assert "## Constatações adicionais" in report
    assert "## Fragmentacao de CNPJs em Sao Paulo" in report
    assert "## Documentos vinculados" in report
    assert "## Conclusao regional" in report
    assert "15/06/2025 a 15/06/2026" in report
    assert "2025-06-15" not in report
    assert "2026-06-15" not in report
