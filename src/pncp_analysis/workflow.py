from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from pncp_analysis.config import AnalysisConfig, CityConfig, load_config
from pncp_analysis.filters import is_sao_paulo_municipal_executive
from pncp_analysis.pncp_client import PncpClient
from pncp_analysis.report import render_report
from pncp_analysis.sampling import deduplicate_records, deterministic_sample
from pncp_analysis.utils import (
    date_for_pncp,
    has_value,
    nested_get,
    parse_control_number,
    read_json,
    utc_now_iso,
    write_json,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = REPO_ROOT / "config" / "analysis.yaml"
RAW_DIR = REPO_ROOT / "data" / "raw"
PROCESSED_DIR = REPO_ROOT / "data" / "processed"
REPORT_PATH = REPO_ROOT / "analise-exploratoria.md"


def build_client(config: AnalysisConfig) -> PncpClient:
    return PncpClient(
        query_bases=config.api.query_bases,
        document_bases=config.api.document_bases,
        page_size=config.api.page_size,
        delay_seconds=config.api.request_delay_seconds,
        retries=config.api.retries,
    )


def collect(config_path: Path = DEFAULT_CONFIG_PATH, limit: int | None = None) -> None:
    config = load_config(config_path)
    client = build_client(config)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    start = date_for_pncp(config.start_date)
    end = date_for_pncp(config.end_date)
    metadata: dict[str, Any] = {
        "generated_at": utc_now_iso(),
        "period": {"start": config.start_date, "end": config.end_date},
        "modality": {"id": config.modality_id, "name": config.modality_name},
        "sources": [],
        "failures": [],
    }

    for city in config.cities:
        print(f"Collecting {city.name} by matrix CNPJ...", flush=True)
        matrix_records = client.fetch_contratacoes(
            start_date=start,
            end_date=end,
            modality_id=config.modality_id,
            cnpj=city.matrix_cnpj,
            limit=limit,
        )
        matrix_path = RAW_DIR / f"{city.slug}_cnpj_{city.matrix_cnpj}_contratacoes.json"
        write_json(matrix_path, matrix_records)
        metadata["sources"].append(
            {
                "city": city.name,
                "kind": "matrix_cnpj",
                "path": str(matrix_path.relative_to(REPO_ROOT)),
                "records": len(matrix_records),
            }
        )
        print(f"Collected {len(matrix_records)} matrix records for {city.name}.", flush=True)

        if city.investigate_fragmentation:
            print(
                (
                    f"Collecting {city.name} municipality scan "
                    f"(max {config.api.municipality_scan_max_pages} pages)..."
                ),
                flush=True,
            )
            municipal_records = client.fetch_contratacoes(
                start_date=start,
                end_date=end,
                modality_id=config.modality_id,
                uf=city.uf,
                ibge=city.ibge,
                limit=limit,
                max_pages=config.api.municipality_scan_max_pages,
            )
            municipal_path = RAW_DIR / f"{city.slug}_municipio_{city.ibge}_contratacoes.json"
            write_json(municipal_path, municipal_records)
            metadata["sources"].append(
                {
                    "city": city.name,
                    "kind": "municipality_scan",
                    "path": str(municipal_path.relative_to(REPO_ROOT)),
                    "records": len(municipal_records),
                    "max_pages": config.api.municipality_scan_max_pages,
                }
            )
            print(
                f"Collected {len(municipal_records)} municipality-scan records for {city.name}.",
                flush=True,
            )

    metadata["failures"] = [failure.__dict__ for failure in client.failures]
    write_json(RAW_DIR / "collection_metadata.json", metadata)


def sample(config_path: Path = DEFAULT_CONFIG_PATH) -> None:
    config = load_config(config_path)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    all_candidates: list[dict[str, Any]] = []
    sampled: list[dict[str, Any]] = []
    sample_limits: list[dict[str, Any]] = []

    for index, city in enumerate(config.cities):
        candidates = load_city_candidates(config, city)
        for record in candidates:
            record["_analysisCity"] = city.name
            record["_analysisCitySlug"] = city.slug

        candidates = deduplicate_records(candidates)
        all_candidates.extend(candidates)

        city_sample = deterministic_sample(
            candidates,
            sample_n=config.sample_n,
            seed=config.seed + index,
        )
        sampled.extend(city_sample)
        if len(candidates) < config.sample_n:
            sample_limits.append(
                {
                    "city": city.name,
                    "available": len(candidates),
                    "requested": config.sample_n,
                }
            )

    write_json(PROCESSED_DIR / "candidate_records.json", all_candidates)
    write_json(PROCESSED_DIR / "sample.json", sampled)
    write_json(PROCESSED_DIR / "sample_limits.json", sample_limits)
    write_sample_csv(PROCESSED_DIR / "sample.csv", sampled)


def analyze(config_path: Path = DEFAULT_CONFIG_PATH, skip_documents: bool = False) -> None:
    config = load_config(config_path)
    client = build_client(config)
    candidates = read_json(PROCESSED_DIR / "candidate_records.json")
    sampled = read_json(PROCESSED_DIR / "sample.json")
    if not isinstance(candidates, list) or not isinstance(sampled, list):
        raise ValueError("Processed candidate/sample files must contain lists")

    document_index: dict[str, list[dict[str, Any]]] = {}
    if skip_documents:
        document_index = {}
    else:
        for record in sampled:
            control = str(record.get("numeroControlePNCP") or "")
            if not control:
                continue
            cnpj = str((record.get("orgaoEntidade") or {}).get("cnpj") or "")
            year = int(record.get("anoCompra") or parse_control_number(control).year)
            sequence = int(record.get("sequencialCompra") or parse_control_number(control).sequence)
            document_index[control] = client.fetch_purchase_documents(
                cnpj=cnpj,
                year=year,
                sequence=sequence,
            )

    metrics = build_metrics(config, candidates, sampled, document_index)
    write_json(RAW_DIR / "sample_documents.json", document_index)
    write_json(PROCESSED_DIR / "metrics.json", metrics)
    write_field_completeness_csv(PROCESSED_DIR / "field_completeness.csv", metrics)
    write_json(
        RAW_DIR / "analysis_failures.json",
        [failure.__dict__ for failure in client.failures],
    )


def report(config_path: Path = DEFAULT_CONFIG_PATH) -> None:
    config = load_config(config_path)
    metrics = read_json(PROCESSED_DIR / "metrics.json")
    sampled = read_json(PROCESSED_DIR / "sample.json")
    REPORT_PATH.write_text(render_report(config, metrics, sampled), encoding="utf-8")


def run_all(config_path: Path = DEFAULT_CONFIG_PATH) -> None:
    collect(config_path)
    sample(config_path)
    analyze(config_path)
    report(config_path)


def load_city_candidates(config: AnalysisConfig, city: CityConfig) -> list[dict[str, Any]]:
    if city.investigate_fragmentation:
        municipal_path = RAW_DIR / f"{city.slug}_municipio_{city.ibge}_contratacoes.json"
        matrix_path = RAW_DIR / f"{city.slug}_cnpj_{city.matrix_cnpj}_contratacoes.json"
        municipal_records = read_json(municipal_path)
        matrix_records = read_json(matrix_path)
        if not isinstance(municipal_records, list):
            raise ValueError(f"Expected list in {municipal_path}")
        if not isinstance(matrix_records, list):
            raise ValueError(f"Expected list in {matrix_path}")

        filtered_municipal = [
            record
            for record in municipal_records
            if isinstance(record, dict)
            and is_sao_paulo_municipal_executive(record, city, config.sao_paulo_filter)
        ]
        matrix = [record for record in matrix_records if isinstance(record, dict)]
        return matrix + filtered_municipal

    matrix_path = RAW_DIR / f"{city.slug}_cnpj_{city.matrix_cnpj}_contratacoes.json"
    records = read_json(matrix_path)
    if not isinstance(records, list):
        raise ValueError(f"Expected list in {matrix_path}")
    return [record for record in records if isinstance(record, dict)]


def build_metrics(
    config: AnalysisConfig,
    candidates: list[dict[str, Any]],
    sampled: list[dict[str, Any]],
    document_index: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    candidate_by_city: dict[str, list[dict[str, Any]]] = defaultdict(list)
    sample_by_city: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in candidates:
        candidate_by_city[str(record.get("_analysisCity") or "")].append(record)
    for record in sampled:
        sample_by_city[str(record.get("_analysisCity") or "")].append(record)

    city_metrics = []
    for city in config.cities:
        city_candidates = candidate_by_city[city.name]
        city_sample = sample_by_city[city.name]
        cnpj_counts = count_cnpjs(city_candidates)
        matrix_count = cnpj_counts.get(city.matrix_cnpj, 0)
        total = len(city_candidates)
        city_metrics.append(
            {
                "city": city.name,
                "candidate_count": total,
                "sample_count": len(city_sample),
                "distinct_cnpj_count": len(cnpj_counts),
                "matrix_cnpj": city.matrix_cnpj,
                "matrix_records": matrix_count,
                "matrix_share": matrix_count / total if total else None,
            }
        )

    field_paths = {
        "Objeto": "objetoCompra",
        "Valor estimado": "valorTotalEstimado",
        "Valor homologado": "valorTotalHomologado",
        "Data de publicacao": "dataPublicacaoPncp",
        "Abertura de proposta": "dataAberturaProposta",
        "Encerramento de proposta": "dataEncerramentoProposta",
        "Unidade": "unidadeOrgao.nomeUnidade",
        "Link de origem": "linkSistemaOrigem",
    }

    field_completeness: list[dict[str, Any]] = []
    for city in config.cities:
        city_sample = sample_by_city[city.name]
        for label, path in field_paths.items():
            present = sum(1 for record in city_sample if has_value(nested_get(record, path)))
            field_completeness.append(
                {
                    "city": city.name,
                    "field": label,
                    "present": present,
                    "sample_count": len(city_sample),
                    "share": present / len(city_sample) if city_sample else None,
                }
            )

        present_docs = sum(
            1
            for record in city_sample
            if has_value(document_index.get(str(record.get("numeroControlePNCP") or ""), []))
        )
        field_completeness.append(
            {
                "city": city.name,
                "field": "Documentos",
                "present": present_docs,
                "sample_count": len(city_sample),
                "share": present_docs / len(city_sample) if city_sample else None,
            }
        )

    sample_rows = []
    for record in sampled:
        control = str(record.get("numeroControlePNCP") or "")
        docs = document_index.get(control, [])
        sample_rows.append(
            {
                "city": record.get("_analysisCity"),
                "numeroControlePNCP": control,
                "cnpj": (record.get("orgaoEntidade") or {}).get("cnpj"),
                "orgao": (record.get("orgaoEntidade") or {}).get("razaoSocial"),
                "unidade": (record.get("unidadeOrgao") or {}).get("nomeUnidade"),
                "dataPublicacaoPncp": record.get("dataPublicacaoPncp"),
                "valorTotalEstimado": record.get("valorTotalEstimado"),
                "valorTotalHomologado": record.get("valorTotalHomologado"),
                "situacaoCompraNome": record.get("situacaoCompraNome"),
                "document_count": len(docs),
                "document_types": sorted(
                    {
                        str(doc.get("tipoDocumentoNome") or doc.get("tipoDocumentoDescricao") or "")
                        for doc in docs
                        if isinstance(doc, dict)
                    }
                ),
                "objetoCompra": record.get("objetoCompra"),
            }
        )

    sao_paulo_candidates = candidate_by_city["Sao Paulo"]
    return {
        "generated_at": utc_now_iso(),
        "period": {"start": config.start_date, "end": config.end_date},
        "modality": {"id": config.modality_id, "name": config.modality_name},
        "sample": {"n": config.sample_n, "seed": config.seed},
        "city_metrics": city_metrics,
        "sao_paulo_top_cnpjs": top_cnpjs(sao_paulo_candidates, limit=10),
        "field_completeness": field_completeness,
        "sample_rows": sample_rows,
        "limitations": [
            "A comparacao e exploratoria e nao representa todos os municipios do Sudeste.",
            (
                "Sao Paulo possui registros municipais distribuidos em varios CNPJs, "
                "o que exige filtro por municipio e orgao."
            ),
            (
                "A varredura municipal de Sao Paulo usa limite operacional de "
                f"{config.api.municipality_scan_max_pages} paginas da API."
            ),
            (
                "A API pode retornar payload HTML de bloqueio com HTTP 200; o coletor "
                "valida Content-Type e registra falhas."
            ),
        ],
    }


def count_cnpjs(records: list[dict[str, Any]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for record in records:
        cnpj = str((record.get("orgaoEntidade") or {}).get("cnpj") or "")
        if cnpj:
            counts[cnpj] += 1
    return counts


def top_cnpjs(records: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    counts = count_cnpjs(records)
    names: dict[str, str] = {}
    for record in records:
        orgao = record.get("orgaoEntidade") or {}
        cnpj = str(orgao.get("cnpj") or "")
        if cnpj and cnpj not in names:
            names[cnpj] = str(orgao.get("razaoSocial") or "")

    return [
        {"cnpj": cnpj, "razao_social": names.get(cnpj, ""), "records": count}
        for cnpj, count in counts.most_common(limit)
    ]


def write_sample_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "city",
        "numeroControlePNCP",
        "cnpj",
        "orgao",
        "unidade",
        "dataPublicacaoPncp",
        "valorTotalEstimado",
        "valorTotalHomologado",
        "situacaoCompraNome",
        "objetoCompra",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for record in rows:
            writer.writerow(
                {
                    "city": record.get("_analysisCity"),
                    "numeroControlePNCP": record.get("numeroControlePNCP"),
                    "cnpj": (record.get("orgaoEntidade") or {}).get("cnpj"),
                    "orgao": (record.get("orgaoEntidade") or {}).get("razaoSocial"),
                    "unidade": (record.get("unidadeOrgao") or {}).get("nomeUnidade"),
                    "dataPublicacaoPncp": record.get("dataPublicacaoPncp"),
                    "valorTotalEstimado": record.get("valorTotalEstimado"),
                    "valorTotalHomologado": record.get("valorTotalHomologado"),
                    "situacaoCompraNome": record.get("situacaoCompraNome"),
                    "objetoCompra": record.get("objetoCompra"),
                }
            )


def write_field_completeness_csv(path: Path, metrics: dict[str, Any]) -> None:
    rows = metrics.get("field_completeness", [])
    if not isinstance(rows, list):
        return

    fields = ["city", "field", "present", "sample_count", "share"]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            if isinstance(row, dict):
                writer.writerow({field: row.get(field) for field in fields})
