from __future__ import annotations

from typing import Any

from pncp_analysis.config import CityConfig, SaoPauloFilterConfig
from pncp_analysis.utils import normalize_text


def is_sao_paulo_municipal_executive(
    record: dict[str, Any],
    city: CityConfig,
    filter_config: SaoPauloFilterConfig,
) -> bool:
    orgao = record.get("orgaoEntidade") or {}
    unidade = record.get("unidadeOrgao") or {}
    if not isinstance(orgao, dict) or not isinstance(unidade, dict):
        return False

    if str(unidade.get("codigoIbge") or "") != city.ibge:
        return False

    esfera = orgao.get("esferaId")
    if esfera is not None and str(esfera) != "M":
        return False

    combined = normalize_text(
        " | ".join(
            [
                str(orgao.get("razaoSocial") or ""),
                str(unidade.get("nomeUnidade") or ""),
            ]
        )
    )

    excluded = [normalize_text(item) for item in filter_config.exclude_indicators]
    if any(indicator in combined for indicator in excluded):
        return False

    included = [normalize_text(item) for item in filter_config.include_indicators]
    return any(indicator in combined for indicator in included)
