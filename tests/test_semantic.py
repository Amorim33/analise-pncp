from __future__ import annotations

import zipfile
from io import BytesIO
from pathlib import Path
from typing import Any

from pncp_analysis.config import (
    AnalysisConfig,
    ApiConfig,
    CityConfig,
    SaoPauloFilterConfig,
    SemanticConfig,
)
from pncp_analysis.pncp_client import BinaryDocument
from pncp_analysis.semantic import (
    aggregate_semantic_metrics,
    extract_text_from_document,
    run_semantic_analysis,
    select_primary_document,
)
from pncp_analysis.utils import read_json, write_json


def test_select_primary_document_prefers_active_revised_edital_with_highest_sequence() -> None:
    selected = select_primary_document(
        "00000000000000-1-000001/2026",
        [
            {
                "statusAtivo": True,
                "tipoDocumentoNome": "Termo de Referencia",
                "titulo": "termo",
                "sequencialDocumento": 3,
                "url": "https://example.test/termo",
            },
            {
                "statusAtivo": True,
                "tipoDocumentoNome": "Edital",
                "titulo": "edital",
                "sequencialDocumento": 1,
                "url": "https://example.test/edital",
            },
            {
                "statusAtivo": True,
                "tipoDocumentoNome": "Edital",
                "titulo": "edital retificado",
                "sequencialDocumento": 2,
                "url": "https://example.test/edital-retificado",
            },
        ],
    )

    doc = selected["selected_document"]
    assert isinstance(doc, dict)
    assert doc["url"] == "https://example.test/edital-retificado"
    assert selected["selection_reason"] == "active_revised_edital_highest_sequence"


def test_extract_text_from_zip_reads_supported_inner_files() -> None:
    payload = BytesIO()
    with zipfile.ZipFile(payload, "w") as archive:
        archive.writestr("edital.txt", "Objeto: compra de materiais escolares\n")
        archive.writestr("imagem.bin", b"\x00\x01")

    extracted = extract_text_from_document(
        filename="arquivo.zip",
        content_type="application/octet-stream",
        body=payload.getvalue(),
    )

    assert extracted.status == "ok"
    assert extracted.file_type == "zip"
    assert "compra de materiais escolares" in extracted.text
    assert "edital.txt" in extracted.sources


def test_aggregate_semantic_metrics_calculates_city_averages() -> None:
    metrics = aggregate_semantic_metrics(
        config=analysis_config(),
        evaluations=[
            {
                "city": "Sao Paulo",
                "status": "evaluated",
                "coerencia_interna": 2,
                "informatividade_do_registro": 4,
                "alinhamento_documento_api": 3,
                "acionabilidade_controle_social": 3,
                "score_medio": 3.0,
            }
        ],
        text_rows=[{"extraction_status": "ok"}],
        skipped=False,
    )

    assert metrics["evaluated_count"] == 1
    assert metrics["overall"]["avg_score_medio"] == 3.0
    assert metrics["by_city"][0]["avg_informatividade_do_registro"] == 4.0


def test_run_semantic_analysis_writes_artifacts_with_fake_services(tmp_path: Path) -> None:
    raw_dir = tmp_path / "data" / "raw"
    processed_dir = tmp_path / "data" / "processed"
    raw_dir.mkdir(parents=True)
    processed_dir.mkdir(parents=True)

    record = sample_record()
    write_json(processed_dir / "document_sample.json", [record])
    write_json(
        raw_dir / "sample_documents.json",
        {
            record["numeroControlePNCP"]: [
                {
                    "statusAtivo": True,
                    "tipoDocumentoNome": "Edital",
                    "titulo": "edital.txt",
                    "sequencialDocumento": 1,
                    "url": "https://example.test/edital.txt",
                }
            ]
        },
    )
    write_json(processed_dir / "metrics.json", {"city_metrics": []})

    metrics = run_semantic_analysis(
        config=analysis_config(cache_dir=str(tmp_path / "cache")),
        raw_dir=raw_dir,
        processed_dir=processed_dir,
        document_sample_path=processed_dir / "document_sample.json",
        document_index_path=raw_dir / "sample_documents.json",
        metrics_path=processed_dir / "metrics.json",
        downloader=FakeDownloader(),
        evaluator=FakeEvaluator(),
    )

    merged = read_json(processed_dir / "metrics.json")
    assert metrics["evaluated_count"] == 1
    assert "semantic_quality" in merged
    assert (processed_dir / "q3_semantic_evaluations.jsonl").exists()
    assert (raw_dir / "q3_codex_responses.jsonl").exists()


class FakeDownloader:
    def fetch_document_binary(self, *, url: str) -> BinaryDocument:
        return BinaryDocument(
            url=url,
            status=200,
            content_type="text/plain",
            filename="edital.txt",
            headers={"content-type": "text/plain"},
            body=b"Objeto: aquisicao de material escolar para escolas municipais.",
        )


class FakeEvaluator:
    def evaluate(self, eval_input: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        assert eval_input["api_record"]["numeroControlePNCP"] == "46395000000139-1-000001/2026"
        return (
            {
                "status": "evaluated",
                "coerencia_interna": 3,
                "informatividade_do_registro": 4,
                "alinhamento_documento_api": 3,
                "acionabilidade_controle_social": 3,
                "resumo": "Registro e edital permitem compreender o objeto.",
                "evidencias": ["Objeto e edital mencionam material escolar."],
                "alertas": [],
            },
            {"model": "codex-subagent", "usage": {"input_tokens": 10}, "output": []},
        )


def sample_record() -> dict[str, Any]:
    return {
        "_analysisCity": "Sao Paulo",
        "numeroControlePNCP": "46395000000139-1-000001/2026",
        "orgaoEntidade": {
            "cnpj": "46395000000139",
            "razaoSocial": "MUNICIPIO DE SAO PAULO",
            "esferaId": "M",
            "poderId": "E",
        },
        "unidadeOrgao": {
            "nomeUnidade": "PMSP - EDUCACAO",
            "municipioNome": "São Paulo",
            "ufSigla": "SP",
            "codigoIbge": "3550308",
        },
        "objetoCompra": "Aquisição de material escolar.",
        "informacaoComplementar": "",
        "modalidadeNome": "Pregão - Eletrônico",
        "situacaoCompraNome": "Divulgada no PNCP",
        "valorTotalEstimado": 1000,
    }


def analysis_config(cache_dir: str = "data/raw/q3_documents") -> AnalysisConfig:
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
            document_cache_dir=cache_dir,
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
