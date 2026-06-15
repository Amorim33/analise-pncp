from pathlib import Path

import pytest

from pncp_analysis.config import AnalysisConfig, ApiConfig, CityConfig, SaoPauloFilterConfig
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
    )

    assert "# Introdução" in markdown
    assert "# Objetivos e método" in markdown
    assert "# Referencial teórico" in markdown
    assert "# Desenvolvimento e análise" in markdown
    assert "# Conclusões" in markdown
    assert "# Apêndice B: declaração de uso de IA" in markdown
    assert "[@curso2026]" in markdown
    assert "[@lei14133]" in markdown


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
    markdown_path = tmp_path / "paper" / "relatorio-final.md"
    tex_path = tmp_path / "paper" / "output" / "relatorio-final.tex"
    pdf_path = tmp_path / "paper" / "output" / "relatorio-final.pdf"

    analysis_config_path.write_text(analysis_yaml(), encoding="utf-8")
    paper_config_path.write_text(paper_yaml(mode="draft"), encoding="utf-8")
    write_json(metrics_path, metrics_payload())
    write_json(collection_path, collection_metadata())
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
                "field": "Documentos",
                "present": 10,
                "sample_count": 10,
                "share": 1.0,
            }
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
                "records": 250,
                "max_pages": 5,
            }
        ]
    }


def analysis_yaml() -> str:
    return """
period:
  start: "2026-01-01"
  end: "2026-05-31"
modality:
  id: 6
  name: "Pregao - Eletronico"
sample:
  n: 10
  seed: 20260608
api:
  query_bases: []
  document_bases: []
  page_size: 50
  municipality_scan_max_pages: 5
  request_delay_seconds: 0
  retries: 1
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
