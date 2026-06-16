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
        "script_execution_events": {
            "events": [
                {
                    "name": "main_successful_collection",
                    "command": "uv run pncp-analysis collect",
                    "started_at": "2026-06-16T02:26:40.029Z",
                    "finished_at": "2026-06-16T03:07:20.784Z",
                    "duration_seconds": 2440.755,
                    "exit_code": 0,
                },
                {
                    "name": "final_snapshot_collection",
                    "command": "uv run pncp-analysis collect",
                    "started_at": "2026-06-16T03:09:59.285Z",
                    "finished_at": "2026-06-16T03:39:48.368Z",
                    "duration_seconds": 1789.083,
                    "exit_code": 0,
                },
                {
                    "name": "final_report_generation",
                    "command": "uv run pncp-analysis report",
                    "started_at": "2026-06-16T03:39:57.332Z",
                    "finished_at": "2026-06-16T03:40:34.661Z",
                    "duration_seconds": 37.329,
                    "exit_code": 0,
                },
                {
                    "name": "pagination_timeout_probe",
                    "command": "uv run python pagination probe",
                    "started_at": "2026-06-16T02:19:15.260Z",
                    "finished_at": "2026-06-16T02:20:17.784Z",
                    "duration_seconds": 62.524,
                    "exit_code": 0,
                },
                {
                    "name": "fallback_run_all",
                    "command": "uv run pncp-analysis run-all",
                    "started_at": "2026-06-16T11:54:56.037Z",
                    "finished_at": "2026-06-16T11:58:33.918Z",
                    "duration_seconds": 217.881,
                    "exit_code": 0,
                },
            ]
        },
    }
    collection_metadata = {
        "duration_seconds": 12.0,
        "sources": [{"records": 19105, "pages_collected": 418}],
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
    assert "Q3." not in report
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
    assert "## Qualidade semantica e informatividade" not in report
    assert "## Conclusao regional" in report
    assert "Historico de execucao" in report
    assert "40min 40.8s" in report
    assert "19105 registros brutos em 418 paginas" in report
    assert "quatro de sete paginas testadas retornaram timeout" in report
    assert "nao foi usada como duracao do experimento principal" in report
    assert "4/4 chamadas foram bem-sucedidas" in report
    assert "15/06/2025 a 15/06/2026" in report
    assert "2025-06-15" not in report
    assert "2026-06-15" not in report
