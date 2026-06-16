from pncp_analysis.config import AnalysisConfig, ApiConfig, SaoPauloFilterConfig, SemanticConfig
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
        semantic=SemanticConfig(
            model="codex-subagent",
            reasoning_effort="medium",
            text_verbosity="low",
            max_document_chars=12000,
            document_cache_dir="data/raw/q3_documents",
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
        "api_experiment": {
            "duration_seconds": 8.0,
            "document_api_performance": {
                "request_count": 4,
                "successful_request_count": 4,
                "failed_attempt_count": 0,
                "average_success_response_seconds": 0.25,
                "max_success_response_seconds": 0.5,
            },
            "document_api_failures": [],
            "observed_experiment_errors": ["HTTP 429 em teste."],
        },
    }
    collection_metadata = {
        "duration_seconds": 12.0,
        "api_performance": {
            "request_count": 5,
            "successful_request_count": 5,
            "failed_attempt_count": 0,
            "average_success_response_seconds": 0.2,
        },
        "failures": [],
    }
    pipeline_metadata = {
        "collection_status": "failed_reused_existing_snapshots",
        "duration_seconds": 20.0,
        "started_at": "2026-06-16T11:54:56+00:00",
        "collection_attempt": {
            "status": "failed",
            "started_at": "2026-06-16T11:54:56+00:00",
            "duration_seconds": 12.0,
            "api_performance": {
                "request_count": 6,
                "successful_request_count": 0,
                "failed_attempt_count": 6,
                "status_counts": {"503": 4},
                "paths": {"/v1/contratacoes/publicacao": 6},
                "failure_examples": [
                    {
                        "attempt": 1,
                        "path": "/v1/contratacoes/publicacao",
                        "status": None,
                        "error": "The read operation timed out",
                    },
                    {
                        "attempt": 2,
                        "path": "/v1/contratacoes/publicacao",
                        "status": 503,
                        "error": "HTTP 503; content-type=text/html; body=<html>",
                    },
                ],
            },
        },
    }

    report = render_report(
        config,
        metrics,
        [],
        collection_metadata=collection_metadata,
        pipeline_metadata=pipeline_metadata,
    )

    assert "# Analise exploratoria do PNCP nas capitais do Sudeste" in report
    assert "## Resumo" in report
    assert "Q1. Ha completude nos dados fornecidos pelo PNCP" in report
    assert "Q2. Os dados das **APIs** do PNCP sao facilmente consumiveis?" in report
    assert "Q3. As respostas da **API** do PNCP sao semanticamente coerentes" in report
    assert "**API**^[**API**:" in report
    assert "**Codex**^[**Codex**:" in report
    assert "**skills**^[**Skills**:" in report
    assert "https://github.com/Amorim33/analise-pncp" in report
    assert "**Codex** como agente de programacao" in report
    assert ".agents/skills/" in report
    assert "## Metodologia" in report
    assert "## Reprodutibilidade e processo agentico" in report
    assert "## Exemplos de registros retornados pela API" in report
    assert "## Constatações adicionais" in report
    assert "## Fragmentacao de CNPJs em Sao Paulo" in report
    assert "## Documentos vinculados" in report
    assert "## Qualidade semantica e informatividade" in report
    assert "## Conclusao regional" in report
    assert "Historico local desta sessao" in report
    assert "HTTP 503 (Service Unavailable)" in report
    assert "2 timeouts" in report
    assert "corpo HTML (`text/html`), nao como JSON" in report
    assert "4/4 chamadas foram bem-sucedidas" in report
    assert "15/06/2025 a 15/06/2026" in report
    assert "2025-06-15" not in report
    assert "2026-06-15" not in report
