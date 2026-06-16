from pncp_analysis.config import AnalysisConfig, ApiConfig, CityConfig, SaoPauloFilterConfig
from pncp_analysis.sampling import deterministic_sample
from pncp_analysis.workflow import build_document_sample, select_analysis_records, write_sample_csv


def test_deterministic_sample_is_stable() -> None:
    records = [{"numeroControlePNCP": f"00000000000000-1-{idx:06d}/2026"} for idx in range(20)]

    first = deterministic_sample(records, sample_n=5, seed=20260608)
    second = deterministic_sample(list(reversed(records)), sample_n=5, seed=20260608)

    assert first == second
    assert len(first) == 5


def test_deterministic_sample_returns_all_when_pool_is_small() -> None:
    records = [{"numeroControlePNCP": "00000000000000-1-000001/2026"}]

    assert deterministic_sample(records, sample_n=10, seed=1) == records


def test_select_analysis_records_returns_all_for_all_strategy() -> None:
    records = [
        {"numeroControlePNCP": "00000000000000-1-000002/2026"},
        {"numeroControlePNCP": "00000000000000-1-000001/2026"},
    ]

    selected = select_analysis_records(analysis_config(), records, seed=1)

    assert [item["numeroControlePNCP"] for item in selected] == [
        "00000000000000-1-000001/2026",
        "00000000000000-1-000002/2026",
    ]


def test_build_document_sample_is_deterministic_and_limited_by_city() -> None:
    records = [
        {
            "_analysisCity": "Sao Paulo",
            "numeroControlePNCP": f"00000000000000-1-{idx:06d}/2026",
        }
        for idx in range(20)
    ]
    config = analysis_config(document_sample_n=5)

    first = build_document_sample(config, records)
    second = build_document_sample(config, list(reversed(records)))

    assert first == second
    assert len(first) == 5


def test_write_sample_csv_normalizes_multiline_text(tmp_path) -> None:
    output = tmp_path / "sample.csv"

    write_sample_csv(
        output,
        [
            {
                "_analysisCity": "Sao Paulo",
                "numeroControlePNCP": "00000000000000-1-000001/2026",
                "orgaoEntidade": {"cnpj": "00000000000000", "razaoSocial": "Orgao  "},
                "unidadeOrgao": {"nomeUnidade": "Unidade\nCentral"},
                "dataPublicacaoPncp": "2026-06-15T10:00:00",
                "valorTotalEstimado": 10,
                "valorTotalHomologado": None,
                "situacaoCompraNome": "Publicada",
                "objetoCompra": "Linha 1\nLinha 2   ",
            }
        ],
    )

    assert "Orgao,Unidade Central" in output.read_text(encoding="utf-8")
    assert "Linha 1 Linha 2  " not in output.read_text(encoding="utf-8")


def analysis_config(document_sample_n: int = 100) -> AnalysisConfig:
    return AnalysisConfig(
        start_date="2025-06-15",
        end_date="2026-06-15",
        modality_id=6,
        modality_name="Pregao - Eletronico",
        sample_strategy="all",
        sample_n=None,
        document_sample_n=document_sample_n,
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
