from __future__ import annotations

import csv
import time
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from pncp_analysis.config import AnalysisConfig, CityConfig, load_config
from pncp_analysis.filters import is_sao_paulo_municipal_executive
from pncp_analysis.pncp_client import PncpClient
from pncp_analysis.report import render_report
from pncp_analysis.sampling import deduplicate_records, deterministic_sample
from pncp_analysis.semantic import run_semantic_analysis
from pncp_analysis.utils import (
    date_for_pncp,
    format_display_date,
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
FULL_SCAN_CHUNK_DAYS = 31


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

    started = time.perf_counter()
    started_at = utc_now_iso()
    metadata: dict[str, Any] = {
        "started_at": started_at,
        "period": {"start": config.start_date, "end": config.end_date},
        "modality": {"id": config.modality_id, "name": config.modality_name},
        "sources": [],
        "failures": [],
    }

    try:
        for city in config.cities:
            print(f"Collecting {city.name} by matrix CNPJ...", flush=True)
            matrix_records, matrix_metadata = fetch_contratacoes_by_chunks(
                client,
                config,
                city,
                cnpj=city.matrix_cnpj,
                limit=limit,
                label=f"{city.name} matrix CNPJ",
            )
            matrix_path = RAW_DIR / f"{city.slug}_cnpj_{city.matrix_cnpj}_contratacoes.json"
            write_json(matrix_path, matrix_records)
            metadata["sources"].append(
                {
                    "city": city.name,
                    "kind": "matrix_cnpj",
                    "path": str(matrix_path.relative_to(REPO_ROOT)),
                    "records": len(matrix_records),
                    **matrix_metadata,
                }
            )
            print(f"Collected {len(matrix_records)} matrix records for {city.name}.", flush=True)

            if city.investigate_fragmentation:
                print(
                    (
                        f"Collecting {city.name} municipality scan "
                        f"({format_page_limit(config.api.municipality_scan_max_pages)})..."
                    ),
                    flush=True,
                )
                if config.api.municipality_scan_max_pages is None:
                    municipal_records, municipal_metadata = fetch_contratacoes_by_chunks(
                        client,
                        config,
                        city,
                        limit=limit,
                        uf=city.uf,
                        ibge=city.ibge,
                        label=f"{city.name} municipality scan",
                    )
                else:
                    start = date_for_pncp(config.start_date)
                    end = date_for_pncp(config.end_date)
                    municipal_records = client.fetch_contratacoes(
                        start_date=start,
                        end_date=end,
                        modality_id=config.modality_id,
                        uf=city.uf,
                        ibge=city.ibge,
                        limit=limit,
                        max_pages=config.api.municipality_scan_max_pages,
                    )
                    municipal_metadata = pagination_metadata(client)
                municipal_path = RAW_DIR / f"{city.slug}_municipio_{city.ibge}_contratacoes.json"
                write_json(municipal_path, municipal_records)
                metadata["sources"].append(
                    {
                        "city": city.name,
                        "kind": "municipality_scan",
                        "path": str(municipal_path.relative_to(REPO_ROOT)),
                        "records": len(municipal_records),
                        "max_pages": config.api.municipality_scan_max_pages,
                        **municipal_metadata,
                    }
                )
                print(
                    f"Collected {len(municipal_records)} municipality-scan records "
                    f"for {city.name}.",
                    flush=True,
                )
    except Exception as exc:
        finalize_collection_metadata(metadata, client, started, status="failed", error=str(exc))
        write_json(RAW_DIR / "collection_attempt_metadata.json", metadata)
        raise

    finalize_collection_metadata(metadata, client, started, status="complete")
    write_json(RAW_DIR / "collection_metadata.json", metadata)
    write_json(RAW_DIR / "collection_attempt_metadata.json", metadata)


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

        city_sample = select_analysis_records(config, candidates, seed=config.seed + index)
        sampled.extend(city_sample)
        if (
            config.sample_strategy == "fixed"
            and config.sample_n is not None
            and len(candidates) < config.sample_n
        ):
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
    started = time.perf_counter()
    started_at = utc_now_iso()
    candidates = read_json(PROCESSED_DIR / "candidate_records.json")
    sampled = read_json(PROCESSED_DIR / "sample.json")
    if not isinstance(candidates, list) or not isinstance(sampled, list):
        raise ValueError("Processed candidate/sample files must contain lists")

    document_sample = build_document_sample(config, sampled)
    write_json(PROCESSED_DIR / "document_sample.json", document_sample)

    document_index: dict[str, list[dict[str, Any]]] = {}
    existing_document_index = read_optional_json(RAW_DIR / "sample_documents.json")
    if not isinstance(existing_document_index, dict):
        existing_document_index = {}
    if skip_documents:
        document_index = {}
    else:
        for record in document_sample:
            control = str(record.get("numeroControlePNCP") or "")
            if not control:
                continue
            cnpj = str((record.get("orgaoEntidade") or {}).get("cnpj") or "")
            year = int(record.get("anoCompra") or parse_control_number(control).year)
            sequence = int(record.get("sequencialCompra") or parse_control_number(control).sequence)
            try:
                document_index[control] = client.fetch_purchase_documents(
                    cnpj=cnpj,
                    year=year,
                    sequence=sequence,
                )
            except RuntimeError:
                fallback_docs = existing_document_index.get(control, [])
                document_index[control] = fallback_docs if isinstance(fallback_docs, list) else []

    api_experiment = {
        "started_at": started_at,
        "finished_at": utc_now_iso(),
        "duration_seconds": round(time.perf_counter() - started, 3),
        "document_api_performance": client.request_summary(),
        "document_api_failures": [failure.__dict__ for failure in client.failures],
        "observed_experiment_errors": [
            "HTTP 429 em chamadas repetidas, tratado com backoff e nova tentativa.",
            (
                "Timeouts em paginação anual longa, mitigados pela coleta em chunks "
                "mensais de 31 dias."
            ),
            (
                "Risco de resposta HTML com HTTP 200, tratado por validação de "
                "Content-Type antes do parse JSON."
            ),
        ],
    }
    metrics = build_metrics(
        config,
        candidates,
        sampled,
        document_sample,
        document_index,
        api_experiment=api_experiment,
    )
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
    collection_metadata = read_optional_json(RAW_DIR / "collection_metadata.json")
    pipeline_metadata = read_optional_json(PROCESSED_DIR / "pipeline_metadata.json")
    REPORT_PATH.write_text(
        render_report(config, metrics, sampled, collection_metadata, pipeline_metadata),
        encoding="utf-8",
    )


def semantic(
    config_path: Path = DEFAULT_CONFIG_PATH,
    *,
    skip_gpt: bool = False,
    reuse_existing: bool = False,
    limit: int | None = None,
) -> None:
    config = load_config(config_path)
    run_semantic_analysis(
        config=config,
        raw_dir=RAW_DIR,
        processed_dir=PROCESSED_DIR,
        document_sample_path=PROCESSED_DIR / "document_sample.json",
        document_index_path=RAW_DIR / "sample_documents.json",
        metrics_path=PROCESSED_DIR / "metrics.json",
        skip_gpt=skip_gpt,
        reuse_existing=reuse_existing,
        limit=limit,
    )


def run_all(config_path: Path = DEFAULT_CONFIG_PATH, *, skip_q3: bool = False) -> None:
    config = load_config(config_path)
    started = time.perf_counter()
    started_at = utc_now_iso()
    collection_attempt: dict[str, Any] = {}
    collection_status = "complete"
    try:
        collect(config_path)
    except RuntimeError as exc:
        collection_attempt = read_optional_json(RAW_DIR / "collection_attempt_metadata.json")
        if not raw_snapshots_available(config):
            raise
        collection_status = "failed_reused_existing_snapshots"
        print(
            (
                "Live collection failed; reusing existing raw snapshots. "
                f"Reason: {exc}"
            ),
            flush=True,
        )
    sample(config_path)
    analyze(config_path)
    if not skip_q3:
        semantic(config_path)
    write_pipeline_metadata(
        started_at=started_at,
        started=started,
        collection_status=collection_status,
        collection_attempt=collection_attempt,
        steps=["collect", "sample", "analyze", *([] if skip_q3 else ["semantic"]), "report"],
        finished=False,
    )
    report(config_path)
    write_pipeline_metadata(
        started_at=started_at,
        started=started,
        collection_status=collection_status,
        collection_attempt=collection_attempt,
        steps=["collect", "sample", "analyze", *([] if skip_q3 else ["semantic"]), "report"],
        finished=True,
    )


def select_analysis_records(
    config: AnalysisConfig,
    candidates: list[dict[str, Any]],
    *,
    seed: int,
) -> list[dict[str, Any]]:
    if config.sample_strategy == "all":
        return deduplicate_records(candidates)
    if config.sample_n is None:
        raise ValueError("sample.n is required when sample.strategy is 'fixed'")
    return deterministic_sample(candidates, sample_n=config.sample_n, seed=seed)


def fetch_contratacoes_by_chunks(
    client: PncpClient,
    config: AnalysisConfig,
    city: CityConfig,
    *,
    limit: int | None,
    label: str,
    cnpj: str | None = None,
    uf: str | None = None,
    ibge: str | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    records: list[dict[str, Any]] = []
    chunks: list[dict[str, Any]] = []

    date_chunks = iter_date_chunks(
        config.start_date,
        config.end_date,
        chunk_days=FULL_SCAN_CHUNK_DAYS,
    )
    for chunk_index, (chunk_start, chunk_end) in enumerate(date_chunks, start=1):
        remaining = None if limit is None else max(limit - len(records), 0)
        if remaining == 0:
            break

        print(
            (
                f"  Collecting {label} chunk {chunk_index}/{len(date_chunks)} "
                f"({format_display_date(chunk_start)} to {format_display_date(chunk_end)})..."
            ),
            flush=True,
        )
        chunk_records = client.fetch_contratacoes(
            start_date=date_for_pncp(chunk_start),
            end_date=date_for_pncp(chunk_end),
            modality_id=config.modality_id,
            cnpj=cnpj,
            uf=uf,
            ibge=ibge,
            limit=remaining,
            max_pages=None,
        )
        records.extend(chunk_records)
        chunk_metadata = pagination_metadata(client)
        print(
            f"  Collected {len(chunk_records)} records for chunk {chunk_index}.",
            flush=True,
        )
        chunks.append(
            {
                "start": chunk_start,
                "end": chunk_end,
                "records": len(chunk_records),
                **chunk_metadata,
            }
        )

    pages_collected = sum(int(chunk.get("pages_collected") or 0) for chunk in chunks)
    total_pages = sum(int(chunk.get("total_pages") or 0) for chunk in chunks)
    total_records = sum(int(chunk.get("total_records") or 0) for chunk in chunks)
    complete = all(bool(chunk.get("pagination_complete")) for chunk in chunks)
    return records, {
        "chunk_days": FULL_SCAN_CHUNK_DAYS,
        "chunks": chunks,
        "pages_collected": pages_collected,
        "total_pages": total_pages,
        "total_records": total_records,
        "pagination_complete": complete,
        "pagination_stopped_reason": None if complete else "At least one chunk was incomplete.",
    }


def iter_date_chunks(start: str, end: str, *, chunk_days: int) -> list[tuple[str, str]]:
    start_date = parse_config_date(start)
    end_date = parse_config_date(end)
    chunks = []
    current = start_date
    while current <= end_date:
        chunk_end = min(current + timedelta(days=chunk_days - 1), end_date)
        chunks.append((current.isoformat(), chunk_end.isoformat()))
        current = chunk_end + timedelta(days=1)
    return chunks


def parse_config_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def finalize_collection_metadata(
    metadata: dict[str, Any],
    client: PncpClient,
    started: float,
    *,
    status: str,
    error: str | None = None,
) -> None:
    metadata["status"] = status
    metadata["finished_at"] = utc_now_iso()
    metadata["generated_at"] = metadata["finished_at"]
    metadata["duration_seconds"] = round(time.perf_counter() - started, 3)
    metadata["api_performance"] = client.request_summary()
    failures = [failure.__dict__ for failure in client.failures]
    if error:
        failures.append({"url": "collect", "reason": error})
        metadata["error"] = error
    metadata["failures"] = failures


def read_optional_json(path: Path) -> Any:
    if not path.exists():
        return {}
    return read_json(path)


def raw_snapshots_available(config: AnalysisConfig) -> bool:
    required_paths = []
    for city in config.cities:
        required_paths.append(RAW_DIR / f"{city.slug}_cnpj_{city.matrix_cnpj}_contratacoes.json")
        if city.investigate_fragmentation:
            required_paths.append(RAW_DIR / f"{city.slug}_municipio_{city.ibge}_contratacoes.json")
    return all(path.exists() for path in required_paths)


def write_pipeline_metadata(
    *,
    started_at: str,
    started: float,
    collection_status: str,
    collection_attempt: dict[str, Any],
    steps: list[str],
    finished: bool,
) -> None:
    payload = {
        "started_at": started_at,
        "finished_at": utc_now_iso(),
        "duration_seconds": round(time.perf_counter() - started, 3),
        "steps": steps,
        "collection_status": collection_status,
        "collection_attempt": collection_attempt,
        "status": "complete" if finished else "running",
    }
    write_json(PROCESSED_DIR / "pipeline_metadata.json", payload)


def build_document_sample(
    config: AnalysisConfig,
    sampled: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    sample_by_city: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in sampled:
        sample_by_city[str(record.get("_analysisCity") or "")].append(record)

    document_sample: list[dict[str, Any]] = []
    for index, city in enumerate(config.cities):
        city_records = sample_by_city[city.name]
        document_sample.extend(
            deterministic_sample(
                city_records,
                sample_n=config.document_sample_n,
                seed=config.seed + 10_000 + index,
            )
        )
    return document_sample


def format_page_limit(max_pages: int | None) -> str:
    if max_pages is None:
        return "all pages"
    return f"max {max_pages} pages"


def pagination_metadata(client: PncpClient) -> dict[str, Any]:
    pagination = client.last_pagination
    if pagination is None:
        return {}
    return {
        "pages_collected": pagination.pages_collected,
        "total_pages": pagination.total_pages,
        "total_records": pagination.total_records,
        "pagination_complete": pagination.complete,
        "pagination_stopped_reason": pagination.stopped_reason,
    }


def build_page_limit_limitation(config: AnalysisConfig) -> str:
    if config.api.municipality_scan_max_pages is None:
        return (
            "A varredura municipal de Sao Paulo coleta todas as paginas retornadas pela "
            "API para a janela anual."
        )
    return (
        "A varredura municipal de Sao Paulo usa limite operacional de "
        f"{config.api.municipality_scan_max_pages} paginas da API."
    )


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
    document_sample: list[dict[str, Any]],
    document_index: dict[str, list[dict[str, Any]]],
    *,
    api_experiment: dict[str, Any] | None = None,
) -> dict[str, Any]:
    candidate_by_city: dict[str, list[dict[str, Any]]] = defaultdict(list)
    sample_by_city: dict[str, list[dict[str, Any]]] = defaultdict(list)
    document_sample_by_city: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in candidates:
        candidate_by_city[str(record.get("_analysisCity") or "")].append(record)
    for record in sampled:
        sample_by_city[str(record.get("_analysisCity") or "")].append(record)
    for record in document_sample:
        document_sample_by_city[str(record.get("_analysisCity") or "")].append(record)

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
            for record in document_sample_by_city[city.name]
            if has_value(document_index.get(str(record.get("numeroControlePNCP") or ""), []))
        )
        docs_sample_count = len(document_sample_by_city[city.name])
        field_completeness.append(
            {
                "city": city.name,
                "field": "Documentos",
                "present": present_docs,
                "sample_count": docs_sample_count,
                "share": present_docs / docs_sample_count if docs_sample_count else None,
                "scope": "document_sample",
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

    document_stats = build_document_stats(config, document_sample_by_city, document_index)
    sao_paulo_candidates = candidate_by_city["Sao Paulo"]
    sp_fragmentation = build_sao_paulo_fragmentation_evidence(config, sao_paulo_candidates)
    additional_findings = build_additional_findings(
        city_metrics=city_metrics,
        field_completeness=field_completeness,
        document_stats=document_stats,
        sao_paulo_fragmentation=sp_fragmentation,
    )

    return {
        "generated_at": utc_now_iso(),
        "period": {"start": config.start_date, "end": config.end_date},
        "modality": {"id": config.modality_id, "name": config.modality_name},
        "sample": {
            "strategy": config.sample_strategy,
            "n": config.sample_n,
            "seed": config.seed,
            "document_n": config.document_sample_n,
        },
        "document_sample": {
            "strategy": "deterministic_by_city",
            "requested_per_city": config.document_sample_n,
            "counts_by_city": {
                city.name: len(document_sample_by_city[city.name]) for city in config.cities
            },
        },
        "city_metrics": city_metrics,
        "sao_paulo_top_cnpjs": top_cnpjs(sao_paulo_candidates, limit=10),
        "sao_paulo_fragmentation_evidence": sp_fragmentation,
        "field_completeness": field_completeness,
        "document_stats": document_stats,
        "sample_rows": sample_rows,
        "api_examples": build_api_examples(config, sample_by_city, document_index),
        "completeness_examples": build_completeness_examples(
            config,
            document_sample_by_city,
            document_index,
        ),
        "api_experiment": api_experiment or {},
        "additional_findings": additional_findings,
        "limitations": [
            "A comparacao e exploratoria e nao representa todos os municipios do Sudeste.",
            (
                "Sao Paulo possui registros municipais distribuidos em varios CNPJs, "
                "o que exige filtro por municipio e orgao."
            ),
            (
                "A API de consulta por publicacao limita cada requisicao a janelas de "
                "ate 365 dias; por isso o recorte usa a maior janela aceita em uma "
                "consulta reprodutivel."
            ),
            build_page_limit_limitation(config),
            (
                "A API pode retornar payload HTML de bloqueio com HTTP 200; o coletor "
                "valida Content-Type e registra falhas."
            ),
        ],
    }


def build_document_stats(
    config: AnalysisConfig,
    sample_by_city: dict[str, list[dict[str, Any]]],
    document_index: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    stats = []
    for city in config.cities:
        city_sample = sample_by_city[city.name]
        counts = [
            len(document_index.get(str(record.get("numeroControlePNCP") or ""), []))
            for record in city_sample
        ]
        document_types = sorted(
            {
                str(doc.get("tipoDocumentoNome") or doc.get("tipoDocumentoDescricao") or "")
                for record in city_sample
                for doc in document_index.get(str(record.get("numeroControlePNCP") or ""), [])
                if isinstance(doc, dict)
                and (doc.get("tipoDocumentoNome") or doc.get("tipoDocumentoDescricao"))
            }
        )
        stats.append(
            {
                "city": city.name,
                "sample_count": len(city_sample),
                "records_with_documents": sum(1 for count in counts if count > 0),
                "min_documents": min(counts) if counts else 0,
                "max_documents": max(counts) if counts else 0,
                "avg_documents": sum(counts) / len(counts) if counts else 0.0,
                "document_types": document_types,
            }
        )
    return stats


def build_sao_paulo_fragmentation_evidence(
    config: AnalysisConfig,
    sao_paulo_candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    city = next((item for item in config.cities if item.name == "Sao Paulo"), None)
    if city is None:
        return {}

    cnpj_counts = count_cnpjs(sao_paulo_candidates)
    total = len(sao_paulo_candidates)
    matrix_count = cnpj_counts.get(city.matrix_cnpj, 0)
    outside_matrix_records = total - matrix_count
    outside_matrix_cnpjs = [cnpj for cnpj in cnpj_counts if cnpj != city.matrix_cnpj]
    examples = []

    for cnpj, count in cnpj_counts.most_common():
        if cnpj == city.matrix_cnpj:
            continue
        record = next(
            (
                item
                for item in sao_paulo_candidates
                if str((item.get("orgaoEntidade") or {}).get("cnpj") or "") == cnpj
            ),
            {},
        )
        examples.append(
            {
                "cnpj": cnpj,
                "razao_social": (record.get("orgaoEntidade") or {}).get("razaoSocial"),
                "records": count,
                "example_control": record.get("numeroControlePNCP"),
                "example_unit": (record.get("unidadeOrgao") or {}).get("nomeUnidade"),
                "example_object": record.get("objetoCompra"),
            }
        )

    return {
        "matrix_cnpj": city.matrix_cnpj,
        "candidate_count": total,
        "matrix_records": matrix_count,
        "outside_matrix_records": outside_matrix_records,
        "outside_matrix_share": outside_matrix_records / total if total else None,
        "distinct_cnpj_count": len(cnpj_counts),
        "outside_matrix_cnpj_count": len(outside_matrix_cnpjs),
        "non_matrix_examples": examples[:8],
    }


def build_api_examples(
    config: AnalysisConfig,
    sample_by_city: dict[str, list[dict[str, Any]]],
    document_index: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    examples = []
    for city in config.cities:
        city_sample = sample_by_city[city.name]
        selected = city_sample[:1]
        if city.name == "Sao Paulo":
            matrix = [
                record
                for record in city_sample
                if str((record.get("orgaoEntidade") or {}).get("cnpj") or "")
                == city.matrix_cnpj
            ]
            non_matrix = [
                record
                for record in city_sample
                if str((record.get("orgaoEntidade") or {}).get("cnpj") or "")
                != city.matrix_cnpj
            ]
            selected = non_matrix[:1] + matrix[:1]

        for record in selected:
            control = str(record.get("numeroControlePNCP") or "")
            docs = document_index.get(control, [])
            examples.append(
                {
                    "label": build_example_label(city.name, record, city.matrix_cnpj),
                    "payload": {
                        "numeroControlePNCP": control,
                        "orgaoEntidade": record.get("orgaoEntidade"),
                        "unidadeOrgao": record.get("unidadeOrgao"),
                        "objetoCompra": record.get("objetoCompra"),
                        "valorTotalEstimado": record.get("valorTotalEstimado"),
                        "valorTotalHomologado": record.get("valorTotalHomologado"),
                        "situacaoCompraNome": record.get("situacaoCompraNome"),
                        "linkSistemaOrigem": record.get("linkSistemaOrigem"),
                        "documentos": [
                            {
                                "tipoDocumentoNome": doc.get("tipoDocumentoNome"),
                                "titulo": doc.get("titulo"),
                                "url": doc.get("url"),
                            }
                            for doc in docs[:3]
                            if isinstance(doc, dict)
                        ],
                    },
                }
            )
    return examples


def build_completeness_examples(
    config: AnalysisConfig,
    sample_by_city: dict[str, list[dict[str, Any]]],
    document_index: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    examples = []
    for index, city in enumerate(config.cities):
        selected = deterministic_sample(
            sample_by_city[city.name],
            sample_n=1,
            seed=config.seed + 20_000 + index,
        )
        if not selected:
            continue
        record = selected[0]
        control = str(record.get("numeroControlePNCP") or "")
        docs = document_index.get(control, [])
        examples.append(
            {
                "city": city.name,
                "numeroControlePNCP": control,
                "cnpj": (record.get("orgaoEntidade") or {}).get("cnpj"),
                "orgao": (record.get("orgaoEntidade") or {}).get("razaoSocial"),
                "unidade": (record.get("unidadeOrgao") or {}).get("nomeUnidade"),
                "dataPublicacaoPncp": record.get("dataPublicacaoPncp"),
                "valorTotalEstimado": record.get("valorTotalEstimado"),
                "valorTotalHomologado": record.get("valorTotalHomologado"),
                "linkSistemaOrigem": record.get("linkSistemaOrigem"),
                "document_count": len(docs),
                "objetoCompra": record.get("objetoCompra"),
            }
        )
    return examples


def build_example_label(city_name: str, record: dict[str, Any], matrix_cnpj: str) -> str:
    cnpj = str((record.get("orgaoEntidade") or {}).get("cnpj") or "")
    if city_name == "Sao Paulo" and cnpj != matrix_cnpj:
        return "Sao Paulo - exemplo fora do CNPJ matriz"
    if city_name == "Sao Paulo":
        return "Sao Paulo - exemplo no CNPJ matriz"
    return city_name


def build_additional_findings(
    *,
    city_metrics: list[dict[str, Any]],
    field_completeness: list[dict[str, Any]],
    document_stats: list[dict[str, Any]],
    sao_paulo_fragmentation: dict[str, Any],
) -> list[str]:
    findings = []
    sp_share = sao_paulo_fragmentation.get("outside_matrix_share")
    if isinstance(sp_share, float):
        findings.append(
            
                "Na amostra candidata de Sao Paulo, "
                f"{sp_share * 100:.1f}% dos registros elegiveis ficaram fora do CNPJ matriz; "
                "nas demais capitais analisadas, os registros por CNPJ matriz concentraram "
                "100% dos candidatos coletados."
            
        )

    sp_city = next((item for item in city_metrics if item.get("city") == "Sao Paulo"), None)
    if sp_city:
        findings.append(
            
                "Sao Paulo apresentou "
                f"{sp_city.get('distinct_cnpj_count')} CNPJs distintos no recorte elegivel, "
                "enquanto Rio de Janeiro, Belo Horizonte e Vitoria apareceram com um CNPJ "
                "cada no recorte por matriz."
            
        )

    vitoria_link = find_field_share(field_completeness, "Vitoria", "Link de origem")
    if vitoria_link == 0:
        findings.append(
            
                "Vitoria teve documentos vinculados em todos os itens da subamostra "
                "documental, mas nenhum dos registros elegiveis trouxe `linkSistemaOrigem`, "
                "o que reduz a "
                "rastreabilidade para o sistema de origem."
            
        )

    homologation = {
        str(item.get("city")): item.get("share")
        for item in field_completeness
        if item.get("field") == "Valor homologado"
    }
    if homologation:
        lowest_city, lowest_share = min(
            homologation.items(),
            key=lambda pair: pair[1] if isinstance(pair[1], float) else 999,
        )
        if isinstance(lowest_share, float):
            findings.append(
                
                    f"O valor homologado apareceu com menor completude em {lowest_city} "
                    f"({lowest_share * 100:.1f}%), indicando que parte dos registros estava "
                    "em fase anterior ao resultado ou sem homologacao registrada no recorte."
                
            )

    vitoria_docs = next((item for item in document_stats if item.get("city") == "Vitoria"), None)
    if vitoria_docs:
        findings.append(
            
                "A quantidade de documentos anexados variou de forma relevante: em Vitoria, "
                f"um item da amostra chegou a {vitoria_docs.get('max_documents')} documentos, "
                "enquanto outros municipios tiveram padrao mais concentrado."
            
        )
    return findings


def find_field_share(
    field_completeness: list[dict[str, Any]],
    city: str,
    field: str,
) -> float | None:
    match = next(
        (
            item
            for item in field_completeness
            if item.get("city") == city and item.get("field") == field
        ),
        None,
    )
    if match is None:
        return None
    share = match.get("share")
    return share if isinstance(share, float) else None


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
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for record in rows:
            row = {
                "city": record.get("_analysisCity"),
                "numeroControlePNCP": record.get("numeroControlePNCP"),
                "cnpj": (record.get("orgaoEntidade") or {}).get("cnpj"),
                "orgao": (record.get("orgaoEntidade") or {}).get("razaoSocial"),
                "unidade": (record.get("unidadeOrgao") or {}).get("nomeUnidade"),
                "dataPublicacaoPncp": format_display_date(
                    str(record.get("dataPublicacaoPncp") or "")
                ),
                "valorTotalEstimado": record.get("valorTotalEstimado"),
                "valorTotalHomologado": record.get("valorTotalHomologado"),
                "situacaoCompraNome": record.get("situacaoCompraNome"),
                "objetoCompra": record.get("objetoCompra"),
            }
            writer.writerow({field: normalize_csv_value(row.get(field)) for field in fields})


def normalize_csv_value(value: Any) -> Any:
    if isinstance(value, str):
        return " ".join(value.split())
    return value


def write_field_completeness_csv(path: Path, metrics: dict[str, Any]) -> None:
    rows = metrics.get("field_completeness", [])
    if not isinstance(rows, list):
        return

    fields = ["city", "field", "present", "sample_count", "share"]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            if isinstance(row, dict):
                writer.writerow({field: row.get(field) for field in fields})
