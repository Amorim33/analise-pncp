from pathlib import Path

import pytest

from pncp_analysis.config import (
    AnalysisConfig,
    ApiConfig,
    CityConfig,
    SaoPauloFilterConfig,
    SemanticConfig,
)
from pncp_analysis.paper import (
    PaperConfig,
    generate_paper,
    render_paper_markdown,
    validate_paper_config,
)
from pncp_analysis.utils import write_json


def test_render_paper_markdown_contains_required_sections_and_citations() -> None:
    markdown = render_paper_markdown(
        analysis_config=analysis_config(),
        paper_config=paper_config(mode="draft"),
        metrics=metrics_payload(),
        sample_rows=[],
        collection_metadata=collection_metadata(),
        pipeline_metadata=pipeline_metadata(),
    )

    assert 'abstract: "Este relatório analisa pregões eletrônicos' in markdown
    assert "# Introdução" in markdown
    assert "# Objetivos e método" in markdown
    assert "# Referencial teórico" in markdown
    assert "# Desenvolvimento e análise" in markdown
    assert "duas questões de pesquisa" in markdown
    assert "Q1. Há completude nos dados fornecidos pelo PNCP" in markdown
    assert "Q2. Os dados das **APIs**^[" in markdown
    assert "Q3." not in markdown
    assert "**APIs**^[**API**:" in markdown
    assert "**Codex**^[**Codex**:" in markdown
    assert "**skills**^[**Skills**:" in markdown
    assert "O PNCP é especialmente relevante" in markdown
    assert "O tema dialoga com a disciplina Governo Aberto" not in markdown
    assert "## Q1: completude dos dados" in markdown
    assert "## Q2: consumo da API" in markdown
    assert "40min 40.8s" in markdown
    assert "reuniu 19105 registros em 418 páginas" in markdown
    assert "quatro de sete páginas testadas demoraram demais" in markdown
    assert "não entrou no tempo do experimento principal" in markdown
    assert "fez 4 de 4 chamadas com sucesso" in markdown
    assert "histórico de execução" not in markdown.lower()
    assert "código de saída" not in markdown
    assert "qualidade semântica" not in markdown
    assert "https://github.com/Amorim33/analise-pncp" in markdown
    assert "O processo foi assistido pelo **Codex**^[" in markdown
    assert ".agents/skills/" in markdown
    assert "Apêndice B" in markdown
    assert "# Conclusões" in markdown
    assert "# Apêndice B: declaração de uso de IA" in markdown
    assert "[@lei14133]" in markdown
    assert "prefeituras das capitais dos estados do sudeste brasileiro" in markdown
    assert "15/06/2025 a 15/06/2026" in markdown
    assert "2025-06-15" not in markdown
    assert "2026-06-15" not in markdown


def test_final_mode_rejects_placeholders_without_override() -> None:
    with pytest.raises(ValueError, match="still contains placeholders"):
        validate_paper_config(paper_config(mode="final"), allow_placeholders=False)


def test_final_mode_accepts_placeholders_with_override() -> None:
    validate_paper_config(paper_config(mode="final"), allow_placeholders=True)


def test_generate_paper_tex_only_writes_tex(tmp_path: Path) -> None:
    analysis_config_path = tmp_path / "analysis.yaml"
    paper_config_path = tmp_path / "paper.yaml"
    metrics_path = tmp_path / "metrics.json"
    sample_path = tmp_path / "sample.csv"
    collection_path = tmp_path / "collection_metadata.json"
    pipeline_path = tmp_path / "pipeline_metadata.json"
    markdown_path = tmp_path / "report" / "relatorio-final.md"
    tex_path = tmp_path / "report" / "output" / "relatorio-final.tex"
    pdf_path = tmp_path / "report" / "output" / "relatorio-final.pdf"

    analysis_config_path.write_text(analysis_yaml(), encoding="utf-8")
    paper_config_path.write_text(paper_yaml(mode="draft"), encoding="utf-8")
    write_json(metrics_path, metrics_payload())
    write_json(collection_path, collection_metadata())
    write_json(pipeline_path, pipeline_metadata())
    sample_path.write_text("city,numeroControlePNCP\nSao Paulo,1\n", encoding="utf-8")

    def fake_tex_runner(markdown: Path, output: Path) -> None:
        output.write_text("% fake tex\n" + markdown.read_text(encoding="utf-8"), encoding="utf-8")

    paths = generate_paper(
        analysis_config_path=analysis_config_path,
        paper_config_path=paper_config_path,
        tex_only=True,
        metrics_path=metrics_path,
        sample_path=sample_path,
        collection_metadata_path=collection_path,
        pipeline_metadata_path=pipeline_path,
        markdown_path=markdown_path,
        tex_path=tex_path,
        pdf_path=pdf_path,
        tex_runner=fake_tex_runner,
    )

    assert paths.tex.exists()
    assert paths.pdf is None
    assert "# Introdução" in paths.markdown.read_text(encoding="utf-8")


def analysis_config() -> AnalysisConfig:
    return AnalysisConfig(
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
        cities=[
            CityConfig(
                name="Sao Paulo",
                slug="sao-paulo",
                uf="SP",
                ibge="3550308",
                matrix_cnpj="46395000000139",
                investigate_fragmentation=True,
            )
        ],
    )


def paper_config(mode: str) -> PaperConfig:
    return PaperConfig(
        mode=mode,
        title="Titulo",
        subtitle="Subtitulo",
        authors=["PREENCHER_NOME"],
        course="Governo Aberto",
        instructor="Jorge Machado",
        institution="USP",
        date="2026-07-01",
        ai_disclosure="Uso de IA declarado.",
    )


def metrics_payload() -> dict[str, object]:
    return {
        "city_metrics": [
            {
                "city": "Sao Paulo",
                "candidate_count": 61,
                "sample_count": 10,
                "distinct_cnpj_count": 10,
                "matrix_records": 6,
                "matrix_share": 0.098,
            }
        ],
        "field_completeness": [
            {
                "city": "Sao Paulo",
                "field": "Objeto",
                "present": 10,
                "sample_count": 10,
                "share": 1.0,
            },
            {
                "city": "Sao Paulo",
                "field": "Valor estimado",
                "present": 10,
                "sample_count": 10,
                "share": 1.0,
            },
            {
                "city": "Sao Paulo",
                "field": "Valor homologado",
                "present": 6,
                "sample_count": 10,
                "share": 0.6,
            },
            {
                "city": "Sao Paulo",
                "field": "Data de publicacao",
                "present": 10,
                "sample_count": 10,
                "share": 1.0,
            },
            {
                "city": "Sao Paulo",
                "field": "Unidade",
                "present": 10,
                "sample_count": 10,
                "share": 1.0,
            },
            {
                "city": "Sao Paulo",
                "field": "Link de origem",
                "present": 9,
                "sample_count": 10,
                "share": 0.9,
            },
            {
                "city": "Sao Paulo",
                "field": "Documentos",
                "present": 10,
                "sample_count": 10,
                "share": 1.0,
            },
        ],
        "document_stats": [
            {
                "city": "Sao Paulo",
                "records_with_documents": 10,
                "sample_count": 10,
                "min_documents": 1,
                "max_documents": 2,
                "avg_documents": 1.2,
            }
        ],
        "additional_findings": ["Achado de teste."],
        "api_examples": [],
        "completeness_examples": [
            {
                "city": "Sao Paulo",
                "numeroControlePNCP": "46395000000139-1-000001/2026",
                "dataPublicacaoPncp": "2026-06-15T10:00:00",
                "valorTotalHomologado": None,
                "linkSistemaOrigem": "https://example.test",
                "document_count": 2,
                "objetoCompra": "Objeto de teste",
            }
        ],
        "api_experiment": {
            "duration_seconds": 8.0,
            "document_api_performance": {
                "request_count": 4,
                "successful_request_count": 4,
                "failed_attempt_count": 0,
                "average_success_response_seconds": 0.25,
            },
            "document_api_failures": [],
            "observed_experiment_errors": ["HTTP 429 em teste."],
        },
        "script_execution_events": script_execution_events(),
        "sample": {"strategy": "all", "n": None, "seed": 20260608, "document_n": 100},
        "document_sample": {
            "strategy": "deterministic_by_city",
            "requested_per_city": 100,
            "counts_by_city": {"Sao Paulo": 61},
        },
        "sao_paulo_fragmentation_evidence": {
            "matrix_cnpj": "46395000000139",
            "candidate_count": 61,
            "matrix_records": 6,
            "outside_matrix_records": 55,
            "outside_matrix_share": 0.902,
            "distinct_cnpj_count": 10,
            "outside_matrix_cnpj_count": 9,
        },
    }


def collection_metadata() -> dict[str, object]:
    return {
        "sources": [
            {
                "city": "Sao Paulo",
                "kind": "municipality_scan",
                "records": 19105,
                "max_pages": None,
                "pages_collected": 418,
                "total_pages": 418,
            }
        ],
        "duration_seconds": 12.0,
        "api_performance": {
            "request_count": 5,
            "successful_request_count": 5,
            "failed_attempt_count": 0,
            "average_success_response_seconds": 0.2,
        },
        "failures": [],
    }


def script_execution_events() -> dict[str, object]:
    return {
        "events": [
            {
                "name": "main_successful_collection",
                "command": "uv run pncp-analysis collect",
                "started_at": "2026-06-16T02:26:40.029Z",
                "finished_at": "2026-06-16T03:07:20.784Z",
                "duration_seconds": 2440.755,
                "exit_code": 0,
                "note": "Coleta completa.",
            },
            {
                "name": "final_snapshot_collection",
                "command": "uv run pncp-analysis collect",
                "started_at": "2026-06-16T03:09:59.285Z",
                "finished_at": "2026-06-16T03:39:48.368Z",
                "duration_seconds": 1789.083,
                "exit_code": 0,
                "note": "Coleta final.",
            },
            {
                "name": "final_report_generation",
                "command": "uv run pncp-analysis sample && uv run pncp-analysis analyze",
                "started_at": "2026-06-16T03:39:57.332Z",
                "finished_at": "2026-06-16T03:40:34.661Z",
                "duration_seconds": 37.329,
                "exit_code": 0,
                "note": "Relatorio final.",
            },
            {
                "name": "pagination_timeout_probe",
                "command": "uv run python pagination probe",
                "started_at": "2026-06-16T02:19:15.260Z",
                "finished_at": "2026-06-16T02:20:17.784Z",
                "duration_seconds": 62.524,
                "exit_code": 0,
                "note": "Quatro de sete paginas com timeout.",
            },
            {
                "name": "fallback_run_all",
                "command": "uv run pncp-analysis run-all",
                "started_at": "2026-06-16T11:54:56.037Z",
                "finished_at": "2026-06-16T11:58:33.918Z",
                "duration_seconds": 217.881,
                "exit_code": 0,
                "note": "Fallback.",
            },
        ]
    }


def pipeline_metadata() -> dict[str, object]:
    return {
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


def analysis_yaml() -> str:
    return """
period:
  start: "2025-06-15"
  end: "2026-06-15"
modality:
  id: 6
  name: "Pregao - Eletronico"
sample:
  strategy: "all"
  n: null
  document_n: 100
  seed: 20260608
api:
  query_bases: []
  document_bases: []
  page_size: 50
  municipality_scan_max_pages: null
  request_delay_seconds: 0
  retries: 1
semantic:
  model: "codex-subagent"
  reasoning_effort: "medium"
  text_verbosity: "low"
  max_document_chars: 12000
  document_cache_dir: "data/raw/q3_documents"
sao_paulo_filter:
  include_indicators: []
  exclude_indicators: []
cities:
  - name: "Sao Paulo"
    slug: "sao-paulo"
    uf: "SP"
    ibge: "3550308"
    matrix_cnpj: "46395000000139"
    investigate_fragmentation: true
"""


def paper_yaml(mode: str) -> str:
    return f"""
mode: "{mode}"
title: "Titulo"
subtitle: "Subtitulo"
authors:
  - "PREENCHER_NOME"
course: "Governo Aberto"
instructor: "Jorge Machado"
institution: "USP"
date: "2026-07-01"
ai_disclosure: "Uso de IA declarado."
"""
