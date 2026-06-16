from pncp_analysis.config import (
    AnalysisConfig,
    ApiConfig,
    CityConfig,
    SaoPauloFilterConfig,
    SemanticConfig,
)
from pncp_analysis.workflow import build_metrics, iter_date_chunks


def test_iter_date_chunks_covers_range_without_overlap() -> None:
    assert iter_date_chunks("2026-01-01", "2026-01-05", chunk_days=2) == [
        ("2026-01-01", "2026-01-02"),
        ("2026-01-03", "2026-01-04"),
        ("2026-01-05", "2026-01-05"),
    ]


def test_build_metrics_uses_configured_fragmentation_city() -> None:
    config = analysis_config()
    candidates = [
        record("Cidade Fragmentada", "11111111111111", "11111111111111-1-000001/2026"),
        record("Cidade Fragmentada", "22222222222222", "22222222222222-1-000002/2026"),
        record("Outra Capital", "33333333333333", "33333333333333-1-000001/2026"),
    ]

    metrics = build_metrics(
        config,
        candidates=candidates,
        sampled=candidates,
        document_sample=[],
        document_index={},
    )

    fragmentation = metrics["sao_paulo_fragmentation_evidence"]
    assert fragmentation["city"] == "Cidade Fragmentada"
    assert fragmentation["matrix_records"] == 1
    assert fragmentation["outside_matrix_records"] == 1
    assert metrics["api_examples"][0]["label"] == (
        "Cidade Fragmentada - exemplo fora do CNPJ matriz"
    )


def record(city: str, cnpj: str, control: str) -> dict[str, object]:
    return {
        "_analysisCity": city,
        "numeroControlePNCP": control,
        "orgaoEntidade": {"cnpj": cnpj, "razaoSocial": f"Orgao {cnpj}"},
        "unidadeOrgao": {"nomeUnidade": "Unidade"},
        "objetoCompra": "Objeto",
        "valorTotalEstimado": 1,
        "dataPublicacaoPncp": "2026-01-01",
    }


def analysis_config() -> AnalysisConfig:
    return AnalysisConfig(
        start_date="2026-01-01",
        end_date="2026-01-05",
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
            request_delay_seconds=0,
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
                name="Cidade Fragmentada",
                slug="cidade-fragmentada",
                uf="SP",
                ibge="3500000",
                matrix_cnpj="11111111111111",
                investigate_fragmentation=True,
            ),
            CityConfig(
                name="Outra Capital",
                slug="outra-capital",
                uf="RJ",
                ibge="3300000",
                matrix_cnpj="33333333333333",
                investigate_fragmentation=False,
            ),
        ],
    )
