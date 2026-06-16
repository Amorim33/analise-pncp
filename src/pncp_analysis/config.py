from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class CityConfig:
    name: str
    slug: str
    uf: str
    ibge: str
    matrix_cnpj: str
    investigate_fragmentation: bool


@dataclass(frozen=True)
class ApiConfig:
    query_bases: list[str]
    document_bases: list[str]
    page_size: int
    municipality_scan_max_pages: int | None
    request_delay_seconds: float
    retries: int


@dataclass(frozen=True)
class SaoPauloFilterConfig:
    include_indicators: list[str]
    exclude_indicators: list[str]


@dataclass(frozen=True)
class SemanticConfig:
    model: str
    reasoning_effort: str
    text_verbosity: str
    max_document_chars: int
    document_cache_dir: str


@dataclass(frozen=True)
class AnalysisConfig:
    start_date: str
    end_date: str
    modality_id: int
    modality_name: str
    sample_strategy: str
    sample_n: int | None
    document_sample_n: int
    seed: int
    api: ApiConfig
    semantic: SemanticConfig
    sao_paulo_filter: SaoPauloFilterConfig
    cities: list[CityConfig]


def load_config(path: Path) -> AnalysisConfig:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"Invalid config file: {path}")

    api = raw["api"]
    period = raw["period"]
    modality = raw["modality"]
    sample = raw["sample"]
    sp_filter = raw["sao_paulo_filter"]
    semantic = raw.get("semantic", {})
    if not isinstance(semantic, dict):
        raise ValueError("semantic config must be an object")

    sample_strategy = str(sample.get("strategy", "fixed"))
    if sample_strategy not in {"fixed", "all"}:
        raise ValueError("sample.strategy must be 'fixed' or 'all'")

    sample_n = optional_int(sample.get("n"))
    if sample_strategy == "fixed" and sample_n is None:
        raise ValueError("sample.n is required when sample.strategy is 'fixed'")

    document_sample_n = optional_int(sample.get("document_n"))
    if document_sample_n is None:
        document_sample_n = sample_n if sample_n is not None else 100

    return AnalysisConfig(
        start_date=str(period["start"]),
        end_date=str(period["end"]),
        modality_id=int(modality["id"]),
        modality_name=str(modality["name"]),
        sample_strategy=sample_strategy,
        sample_n=sample_n,
        document_sample_n=document_sample_n,
        seed=int(sample["seed"]),
        api=ApiConfig(
            query_bases=list_of_str(api["query_bases"]),
            document_bases=list_of_str(api["document_bases"]),
            page_size=int(api["page_size"]),
            municipality_scan_max_pages=optional_int(api["municipality_scan_max_pages"]),
            request_delay_seconds=float(api["request_delay_seconds"]),
            retries=int(api["retries"]),
        ),
        semantic=SemanticConfig(
            model=str(semantic.get("model", "codex-subagent")),
            reasoning_effort=str(semantic.get("reasoning_effort", "medium")),
            text_verbosity=str(semantic.get("text_verbosity", "low")),
            max_document_chars=int(semantic.get("max_document_chars", 12000)),
            document_cache_dir=str(semantic.get("document_cache_dir", "data/raw/q3_documents")),
        ),
        sao_paulo_filter=SaoPauloFilterConfig(
            include_indicators=list_of_str(sp_filter["include_indicators"]),
            exclude_indicators=list_of_str(sp_filter["exclude_indicators"]),
        ),
        cities=[
            CityConfig(
                name=str(city["name"]),
                slug=str(city["slug"]),
                uf=str(city["uf"]),
                ibge=str(city["ibge"]),
                matrix_cnpj=str(city["matrix_cnpj"]),
                investigate_fragmentation=bool(city["investigate_fragmentation"]),
            )
            for city in raw["cities"]
        ],
    )


def list_of_str(value: Any) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"Expected a list, got {type(value).__name__}")
    return [str(item) for item in value]


def optional_int(value: Any) -> int | None:
    if value is None:
        return None
    return int(value)
