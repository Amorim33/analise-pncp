from pncp_analysis.config import CityConfig, SaoPauloFilterConfig
from pncp_analysis.filters import is_sao_paulo_municipal_executive

CITY = CityConfig(
    name="Sao Paulo",
    slug="sao-paulo",
    uf="SP",
    ibge="3550308",
    matrix_cnpj="46395000000139",
    investigate_fragmentation=True,
)

FILTER = SaoPauloFilterConfig(
    include_indicators=["PMSP", "FUNDO MUNICIPAL", "SECRETARIA MUNICIPAL"],
    exclude_indicators=["CAMARA MUNICIPAL", "CMSP", "PODER LEGISLATIVO"],
)


def test_sao_paulo_filter_includes_municipal_executive_unit() -> None:
    record = {
        "orgaoEntidade": {
            "cnpj": "13864377000130",
            "razaoSocial": "FUNDO MUNICIPAL DE SAUDE - FMS",
            "esferaId": "M",
        },
        "unidadeOrgao": {
            "codigoIbge": "3550308",
            "nomeUnidade": "PMSP - SECRETARIA MUNICIPAL DE SAUDE",
        },
    }

    assert is_sao_paulo_municipal_executive(record, CITY, FILTER)


def test_sao_paulo_filter_excludes_legislative_unit() -> None:
    record = {
        "orgaoEntidade": {
            "cnpj": "50176288000128",
            "razaoSocial": "SAO PAULO CAMARA MUNICIPAL",
            "esferaId": "M",
        },
        "unidadeOrgao": {
            "codigoIbge": "3550308",
            "nomeUnidade": "PMSP - CMSP - CAMARA MUNICIPAL DE SAO PAULO",
        },
    }

    assert not is_sao_paulo_municipal_executive(record, CITY, FILTER)


def test_sao_paulo_filter_excludes_other_sphere() -> None:
    record = {
        "orgaoEntidade": {
            "cnpj": "00000000000100",
            "razaoSocial": "SECRETARIA MUNICIPAL FAKE",
            "esferaId": "F",
        },
        "unidadeOrgao": {
            "codigoIbge": "3550308",
            "nomeUnidade": "PMSP - SECRETARIA MUNICIPAL FAKE",
        },
    }

    assert not is_sao_paulo_municipal_executive(record, CITY, FILTER)
