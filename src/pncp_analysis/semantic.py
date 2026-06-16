from __future__ import annotations

import hashlib
import html
import json
import re
import zipfile
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any, Protocol, cast

from pncp_analysis.config import AnalysisConfig
from pncp_analysis.pncp_client import BinaryDocument, PncpClient
from pncp_analysis.utils import normalize_text, read_json, utc_now_iso, write_json

PROMPT_VERSION = "q3-semantic-v1"
SCHEMA_VERSION = "q3-semantic-schema-v1"
SCORE_FIELDS = [
    "coerencia_interna",
    "informatividade_do_registro",
    "alinhamento_documento_api",
    "acionabilidade_controle_social",
]
REVISION_MARKERS = ("REPUBLICADO", "RETIFICADO", "CONSOLIDADO", "ATUALIZADO")


class DocumentDownloader(Protocol):
    def fetch_document_binary(self, *, url: str) -> BinaryDocument:
        raise NotImplementedError


class SemanticEvaluator(Protocol):
    def evaluate(self, eval_input: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        raise NotImplementedError


@dataclass(frozen=True)
class TextExtraction:
    text: str
    status: str
    file_type: str
    sources: list[str]
    error: str | None = None


def run_semantic_analysis(
    *,
    config: AnalysisConfig,
    raw_dir: Path,
    processed_dir: Path,
    document_sample_path: Path,
    document_index_path: Path,
    metrics_path: Path,
    downloader: DocumentDownloader | None = None,
    evaluator: SemanticEvaluator | None = None,
    skip_gpt: bool = False,
    reuse_existing: bool = False,
    limit: int | None = None,
) -> dict[str, Any]:
    q3_metrics_path = processed_dir / "q3_semantic_metrics.json"
    if reuse_existing and q3_metrics_path.exists():
        metrics = read_json(q3_metrics_path)
        if not isinstance(metrics, dict):
            raise ValueError(f"Expected object in {q3_metrics_path}")
        merge_semantic_metrics(metrics_path, metrics)
        return metrics

    document_sample = read_json(document_sample_path)
    document_index = read_json(document_index_path)
    if not isinstance(document_sample, list) or not isinstance(document_index, dict):
        raise ValueError(
            "Q3 expects document_sample.json as list and sample_documents.json as object"
        )

    selected_records = [item for item in document_sample if isinstance(item, dict)]
    if limit is not None:
        selected_records = selected_records[:limit]

    resolved_downloader = downloader or build_downloader(config)
    resolved_evaluator = evaluator
    if resolved_evaluator is None:
        skip_gpt = True

    selection_rows: list[dict[str, Any]] = []
    manifest_rows: list[dict[str, Any]] = []
    text_rows: list[dict[str, Any]] = []
    input_rows: list[dict[str, Any]] = []
    response_rows: list[dict[str, Any]] = []
    evaluation_rows: list[dict[str, Any]] = []

    cache_dir = Path(config.semantic.document_cache_dir)
    if not cache_dir.is_absolute():
        cache_dir = raw_dir.parent.parent / cache_dir
    cache_dir.mkdir(parents=True, exist_ok=True)

    for record in selected_records:
        control = str(record.get("numeroControlePNCP") or "")
        docs = document_index.get(control, [])
        docs_list = (
            [item for item in docs if isinstance(item, dict)]
            if isinstance(docs, list)
            else []
        )
        selection = select_primary_document(control, docs_list)
        selection_rows.append(selection)

        extraction = TextExtraction(
            text="",
            status="no_document",
            file_type="none",
            sources=[],
            error=None,
        )
        if isinstance(selection.get("selected_document"), dict):
            selected_doc = selection["selected_document"]
            try:
                binary = download_or_read_cached(
                    resolved_downloader,
                    selected_doc=selected_doc,
                    cache_dir=cache_dir,
                )
                manifest_rows.append(build_manifest_row(control, selected_doc, binary))
                extraction = extract_text_from_document(
                    filename=binary.filename or str(selected_doc.get("titulo") or ""),
                    content_type=binary.content_type,
                    body=binary.body,
                )
            except Exception as exc:  # noqa: BLE001 - preserve per-document failure details.
                manifest_rows.append(
                    {
                        "numeroControlePNCP": control,
                        "url": selected_doc.get("url") or selected_doc.get("uri"),
                        "status": "download_error",
                        "error": str(exc),
                    }
                )
                extraction = TextExtraction(
                    text="",
                    status="download_error",
                    file_type="unknown",
                    sources=[],
                    error=str(exc),
                )

        text_row = build_text_row(control, record, selection, extraction)
        text_rows.append(text_row)
        eval_input = build_eval_input(
            record=record,
            selection=selection,
            text_row=text_row,
            max_document_chars=config.semantic.max_document_chars,
        )
        input_hash = sha256_text(stable_json(eval_input))
        input_rows.append(
            {
                "numeroControlePNCP": control,
                "input_hash": input_hash,
                "prompt_version": PROMPT_VERSION,
                "schema_version": SCHEMA_VERSION,
                "input": eval_input,
            }
        )

        if skip_gpt:
            evaluation_rows.append(build_pending_evaluation(record, input_hash, text_row))
            continue
        if resolved_evaluator is None:
            raise RuntimeError("Q3 semantic evaluator was not configured")

        normalized, raw_response = resolved_evaluator.evaluate(eval_input)
        response_hash = sha256_text(stable_json(raw_response))
        response_rows.append(
            {
                "numeroControlePNCP": control,
                "input_hash": input_hash,
                "response_hash": response_hash,
                "model": raw_response.get("model", config.semantic.model),
                "system_fingerprint": raw_response.get("system_fingerprint"),
                "usage": raw_response.get("usage", {}),
                "response": raw_response,
            }
        )
        evaluation_rows.append(
            normalize_evaluation(
                record=record,
                input_hash=input_hash,
                response_hash=response_hash,
                text_row=text_row,
                evaluation=normalized,
                model=str(raw_response.get("model") or config.semantic.model),
            )
        )

    write_json(processed_dir / "q3_document_selection.json", selection_rows)
    write_json(raw_dir / "q3_documents_manifest.json", manifest_rows)
    write_jsonl(processed_dir / "q3_document_texts.jsonl", text_rows)
    write_jsonl(processed_dir / "q3_eval_inputs.jsonl", input_rows)
    write_jsonl(raw_dir / "q3_codex_responses.jsonl", response_rows)
    write_jsonl(processed_dir / "q3_semantic_evaluations.jsonl", evaluation_rows)

    semantic_metrics = aggregate_semantic_metrics(
        config=config,
        evaluations=evaluation_rows,
        text_rows=text_rows,
        skipped=skip_gpt,
    )
    write_json(q3_metrics_path, semantic_metrics)
    merge_semantic_metrics(metrics_path, semantic_metrics)
    return semantic_metrics


def build_downloader(config: AnalysisConfig) -> PncpClient:
    return PncpClient(
        query_bases=config.api.query_bases,
        document_bases=config.api.document_bases,
        page_size=config.api.page_size,
        delay_seconds=config.api.request_delay_seconds,
        retries=config.api.retries,
    )


def select_primary_document(control: str, docs: list[dict[str, Any]]) -> dict[str, Any]:
    candidates = [doc for doc in docs if isinstance(doc, dict)]
    if not candidates:
        return {
            "numeroControlePNCP": control,
            "available_documents": 0,
            "selected_document": None,
            "selection_reason": "no_document",
        }

    ranked = sorted(candidates, key=document_priority, reverse=True)
    selected = ranked[0]
    return {
        "numeroControlePNCP": control,
        "available_documents": len(candidates),
        "selected_document": selected,
        "selection_reason": selection_reason(selected),
    }


def document_priority(doc: dict[str, Any]) -> tuple[int, int, int, int]:
    active = 1 if doc.get("statusAtivo", True) else 0
    type_text = normalize_text(
        " ".join(
            [
                str(doc.get("tipoDocumentoNome") or ""),
                str(doc.get("tipoDocumentoDescricao") or ""),
            ]
        )
    )
    title = normalize_text(str(doc.get("titulo") or ""))
    is_edital = 1 if "EDITAL" in type_text else 0
    is_revision = 1 if any(marker in title for marker in REVISION_MARKERS) else 0
    sequence = optional_int(doc.get("sequencialDocumento")) or 0
    return (active, is_edital, is_revision, sequence)


def selection_reason(doc: dict[str, Any]) -> str:
    priority = document_priority(doc)
    if priority[1] and priority[2]:
        return "active_revised_edital_highest_sequence"
    if priority[1]:
        return "active_edital_highest_sequence"
    return "active_document_highest_sequence"


def download_or_read_cached(
    downloader: DocumentDownloader,
    *,
    selected_doc: dict[str, Any],
    cache_dir: Path,
) -> BinaryDocument:
    url = str(selected_doc.get("url") or selected_doc.get("uri") or "")
    if not url:
        raise ValueError("Selected document has no url/uri")
    binary = downloader.fetch_document_binary(url=url)
    cache_doc = dict(selected_doc)
    if binary.filename:
        cache_doc["titulo"] = binary.filename
    cache_path = cache_dir / cache_filename(url, cache_doc)
    cache_path.write_bytes(binary.body)
    return binary


def cache_filename(url: str, selected_doc: dict[str, Any]) -> str:
    digest = sha256_text(url)[:16]
    filename = str(selected_doc.get("titulo") or "documento.bin")
    clean = re.sub(r"[^A-Za-z0-9_.-]+", "_", filename).strip("._") or "documento.bin"
    return f"{digest}_{clean[:80]}"


def build_manifest_row(
    control: str,
    selected_doc: dict[str, Any],
    binary: BinaryDocument,
) -> dict[str, Any]:
    return {
        "numeroControlePNCP": control,
        "url": binary.url,
        "status": binary.status,
        "content_type": binary.content_type,
        "filename": binary.filename,
        "content_length": len(binary.body),
        "sha256": sha256_bytes(binary.body),
        "headers": binary.headers,
        "document_title": selected_doc.get("titulo"),
        "document_type": selected_doc.get("tipoDocumentoNome")
        or selected_doc.get("tipoDocumentoDescricao"),
    }


def extract_text_from_document(
    *,
    filename: str,
    content_type: str,
    body: bytes,
    source_name: str | None = None,
    depth: int = 0,
) -> TextExtraction:
    name = source_name or filename or "document"
    suffix = Path(filename.lower()).suffix
    try:
        if suffix == ".pdf" or body.startswith(b"%PDF"):
            return extract_pdf_text(body, name)
        if suffix == ".docx":
            return extract_docx_text(body, name)
        if suffix in {".txt", ".csv", ".html", ".htm"} or content_type.startswith("text/"):
            return extract_plain_text(body, name, suffix or content_type)
        if suffix == ".zip" or (depth == 0 and zipfile.is_zipfile(BytesIO(body))):
            return extract_zip_text(body, name, depth=depth)
    except Exception as exc:  # noqa: BLE001 - record extraction failures per file.
        return TextExtraction(
            text="",
            status="extract_error",
            file_type=suffix.lstrip(".") or "unknown",
            sources=[name],
            error=str(exc),
        )
    return TextExtraction(
        text="",
        status="unsupported_format",
        file_type=suffix.lstrip(".") or content_type or "unknown",
        sources=[name],
        error="Unsupported document format for text extraction.",
    )


def extract_pdf_text(body: bytes, source: str) -> TextExtraction:
    from pypdf import PdfReader

    reader = PdfReader(BytesIO(body))
    parts = [page.extract_text() or "" for page in reader.pages]
    text = normalize_extracted_text("\n".join(parts))
    return TextExtraction(
        text=text,
        status="ok" if text else "empty_text",
        file_type="pdf",
        sources=[source],
    )


def extract_docx_text(body: bytes, source: str) -> TextExtraction:
    from docx import Document

    document = Document(BytesIO(body))
    text = normalize_extracted_text("\n".join(paragraph.text for paragraph in document.paragraphs))
    return TextExtraction(
        text=text,
        status="ok" if text else "empty_text",
        file_type="docx",
        sources=[source],
    )


def extract_plain_text(body: bytes, source: str, file_type: str) -> TextExtraction:
    decoded = body.decode("utf-8", errors="replace")
    if file_type in {".html", ".htm"} or "<html" in decoded[:500].lower():
        decoded = re.sub(r"<[^>]+>", " ", decoded)
        decoded = html.unescape(decoded)
        file_type = "html"
    text = normalize_extracted_text(decoded)
    return TextExtraction(
        text=text,
        status="ok" if text else "empty_text",
        file_type=file_type.lstrip("."),
        sources=[source],
    )


def extract_zip_text(body: bytes, source: str, *, depth: int) -> TextExtraction:
    if depth > 1:
        return TextExtraction(
            text="",
            status="unsupported_format",
            file_type="zip",
            sources=[source],
            error="Nested ZIP depth limit reached.",
        )
    chunks = []
    sources = [source]
    errors = []
    with zipfile.ZipFile(BytesIO(body)) as archive:
        for member in sorted(archive.namelist()):
            if member.endswith("/") or member.startswith("__MACOSX/"):
                continue
            payload = archive.read(member)
            extracted = extract_text_from_document(
                filename=member,
                content_type="",
                body=payload,
                source_name=member,
                depth=depth + 1,
            )
            sources.extend(extracted.sources)
            if extracted.text:
                chunks.append(f"--- {member} ---\n{extracted.text}")
            if extracted.error:
                errors.append(f"{member}: {extracted.error}")
    text = normalize_extracted_text("\n\n".join(chunks))
    return TextExtraction(
        text=text,
        status="ok" if text else "empty_text",
        file_type="zip",
        sources=unique_strings(sources),
        error="; ".join(errors) if errors else None,
    )


def normalize_extracted_text(value: str) -> str:
    return "\n".join(line.strip() for line in value.replace("\r", "\n").split("\n") if line.strip())


def build_text_row(
    control: str,
    record: dict[str, Any],
    selection: dict[str, Any],
    extraction: TextExtraction,
) -> dict[str, Any]:
    selected = selection.get("selected_document")
    selected_doc = selected if isinstance(selected, dict) else {}
    return {
        "numeroControlePNCP": control,
        "city": record.get("_analysisCity"),
        "document_url": selected_doc.get("url") or selected_doc.get("uri"),
        "document_title": selected_doc.get("titulo"),
        "document_type": selected_doc.get("tipoDocumentoNome")
        or selected_doc.get("tipoDocumentoDescricao"),
        "extraction_status": extraction.status,
        "file_type": extraction.file_type,
        "sources": extraction.sources,
        "char_count": len(extraction.text),
        "text_sha256": sha256_text(extraction.text) if extraction.text else None,
        "error": extraction.error,
        "text": extraction.text,
    }


def build_eval_input(
    *,
    record: dict[str, Any],
    selection: dict[str, Any],
    text_row: dict[str, Any],
    max_document_chars: int,
) -> dict[str, Any]:
    text = str(text_row.get("text") or "")
    return {
        "question": "As respostas da API sao semanticamente coerentes e informativas?",
        "rubric": {
            "scale": "0 a 4",
            "scores": SCORE_FIELDS,
            "evidence_rule": (
                "Avalie somente o registro da API, metadados do documento principal "
                "e texto extraido. Nao use conhecimento externo como fonte de verdade."
            ),
        },
        "api_record": compact_record(record),
        "document_selection": {
            "selection_reason": selection.get("selection_reason"),
            "available_documents": selection.get("available_documents"),
            "document_title": text_row.get("document_title"),
            "document_type": text_row.get("document_type"),
            "document_url": text_row.get("document_url"),
            "extraction_status": text_row.get("extraction_status"),
            "char_count": text_row.get("char_count"),
        },
        "document_text_excerpt": text[:max_document_chars],
    }


def compact_record(record: dict[str, Any]) -> dict[str, Any]:
    raw_orgao = record.get("orgaoEntidade")
    raw_unidade = record.get("unidadeOrgao")
    orgao = cast(dict[str, Any], raw_orgao) if isinstance(raw_orgao, dict) else {}
    unidade = cast(dict[str, Any], raw_unidade) if isinstance(raw_unidade, dict) else {}
    return {
        "city": record.get("_analysisCity"),
        "numeroControlePNCP": record.get("numeroControlePNCP"),
        "cnpj": orgao.get("cnpj"),
        "razaoSocial": orgao.get("razaoSocial"),
        "esferaId": orgao.get("esferaId"),
        "poderId": orgao.get("poderId"),
        "unidade": unidade.get("nomeUnidade"),
        "municipioNome": unidade.get("municipioNome"),
        "ufSigla": unidade.get("ufSigla"),
        "codigoIbge": unidade.get("codigoIbge"),
        "objetoCompra": record.get("objetoCompra"),
        "informacaoComplementar": record.get("informacaoComplementar"),
        "modalidadeNome": record.get("modalidadeNome"),
        "modoDisputaNome": record.get("modoDisputaNome"),
        "situacaoCompraNome": record.get("situacaoCompraNome"),
        "dataPublicacaoPncp": record.get("dataPublicacaoPncp"),
        "dataAberturaProposta": record.get("dataAberturaProposta"),
        "dataEncerramentoProposta": record.get("dataEncerramentoProposta"),
        "valorTotalEstimado": record.get("valorTotalEstimado"),
        "valorTotalHomologado": record.get("valorTotalHomologado"),
        "linkSistemaOrigem": record.get("linkSistemaOrigem"),
    }


def semantic_system_prompt() -> str:
    return (
        "Voce avalia qualidade informacional de registros do PNCP para controle social. "
        "Use apenas o JSON da API e o texto extraido do documento principal. "
        "Atribua notas inteiras de 0 a 4 para cada criterio, registre evidencias curtas "
        "e sinalize contradicoes ou texto insuficiente."
    )


def semantic_json_schema() -> dict[str, Any]:
    score = {"type": "integer", "minimum": 0, "maximum": 4}
    return {
        "type": "object",
        "properties": {
            "status": {"type": "string", "enum": ["evaluated", "insufficient_text"]},
            "coerencia_interna": score,
            "informatividade_do_registro": score,
            "alinhamento_documento_api": score,
            "acionabilidade_controle_social": score,
            "resumo": {"type": "string"},
            "evidencias": {"type": "array", "items": {"type": "string"}},
            "alertas": {"type": "array", "items": {"type": "string"}},
        },
        "required": [
            "status",
            *SCORE_FIELDS,
            "resumo",
            "evidencias",
            "alertas",
        ],
        "additionalProperties": False,
    }


def extract_output_text(raw_response: dict[str, Any]) -> str:
    output = raw_response.get("output", [])
    if not isinstance(output, list):
        return ""
    parts = []
    for item in output:
        if not isinstance(item, dict):
            continue
        content = item.get("content", [])
        if not isinstance(content, list):
            continue
        for content_item in content:
            if isinstance(content_item, dict) and isinstance(content_item.get("text"), str):
                parts.append(content_item["text"])
    return "\n".join(parts)


def normalize_evaluation(
    *,
    record: dict[str, Any],
    input_hash: str,
    response_hash: str,
    text_row: dict[str, Any],
    evaluation: dict[str, Any],
    model: str,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "numeroControlePNCP": record.get("numeroControlePNCP"),
        "city": record.get("_analysisCity"),
        "status": str(evaluation.get("status") or "evaluated"),
        "input_hash": input_hash,
        "response_hash": response_hash,
        "model": model,
        "prompt_version": PROMPT_VERSION,
        "schema_version": SCHEMA_VERSION,
        "extraction_status": text_row.get("extraction_status"),
        "text_sha256": text_row.get("text_sha256"),
        "resumo": evaluation.get("resumo", ""),
        "evidencias": as_str_list(evaluation.get("evidencias")),
        "alertas": as_str_list(evaluation.get("alertas")),
    }
    for field in SCORE_FIELDS:
        row[field] = bounded_score(evaluation.get(field))
    row["score_medio"] = average_scores(row)
    return row


def build_pending_evaluation(
    record: dict[str, Any],
    input_hash: str,
    text_row: dict[str, Any],
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "numeroControlePNCP": record.get("numeroControlePNCP"),
        "city": record.get("_analysisCity"),
        "status": "not_evaluated",
        "input_hash": input_hash,
        "response_hash": None,
        "model": None,
        "prompt_version": PROMPT_VERSION,
        "schema_version": SCHEMA_VERSION,
        "extraction_status": text_row.get("extraction_status"),
        "text_sha256": text_row.get("text_sha256"),
        "resumo": "Avaliacao Codex subagent ainda nao executada.",
        "evidencias": [],
        "alertas": [],
        "score_medio": None,
    }
    for field in SCORE_FIELDS:
        row[field] = None
    return row


def aggregate_semantic_metrics(
    *,
    config: AnalysisConfig,
    evaluations: list[dict[str, Any]],
    text_rows: list[dict[str, Any]],
    skipped: bool,
) -> dict[str, Any]:
    by_city: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in evaluations:
        by_city[str(row.get("city") or "")].append(row)

    overall = aggregate_rows(evaluations)
    return {
        "generated_at": utc_now_iso(),
        "question": "Q3. As respostas da API sao semanticamente coerentes e informativas?",
        "model": config.semantic.model,
        "reasoning_effort": config.semantic.reasoning_effort,
        "text_verbosity": config.semantic.text_verbosity,
        "prompt_version": PROMPT_VERSION,
        "schema_version": SCHEMA_VERSION,
        "pending_codex_evaluation": skipped,
        "sample_count": len(evaluations),
        "scored_count": overall.get("scored_count", 0),
        "evaluated_count": count_status(evaluations, "evaluated"),
        "not_evaluated_count": count_status(evaluations, "not_evaluated"),
        "insufficient_text_count": count_status(evaluations, "insufficient_text"),
        "extraction_status_counts": count_values(text_rows, "extraction_status"),
        "overall": overall,
        "by_city": [
            {"city": city, **aggregate_rows(rows)}
            for city, rows in sorted(by_city.items())
            if city
        ],
        "examples": semantic_examples(evaluations),
        "limitations": semantic_limitations(text_rows, skipped),
    }


def aggregate_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    evaluated = [row for row in rows if row.get("status") == "evaluated"]
    scored = [row for row in rows if isinstance(row.get("score_medio"), (int, float))]
    result: dict[str, Any] = {
        "sample_count": len(rows),
        "scored_count": len(scored),
        "evaluated_count": len(evaluated),
        "insufficient_text_count": count_status(rows, "insufficient_text"),
    }
    for field in [*SCORE_FIELDS, "score_medio"]:
        values = [float(row[field]) for row in scored if isinstance(row.get(field), (int, float))]
        result[f"avg_{field}"] = round(sum(values) / len(values), 2) if values else None
    return result


def semantic_examples(evaluations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    for row in evaluations:
        if row.get("status") != "evaluated":
            continue
        alerts = row.get("alertas", [])
        if not alerts and len(examples) >= 4:
            continue
        examples.append(
            {
                "city": row.get("city"),
                "numeroControlePNCP": row.get("numeroControlePNCP"),
                "score_medio": row.get("score_medio"),
                "resumo": row.get("resumo"),
                "alertas": alerts,
            }
        )
        if len(examples) >= 6:
            break
    return examples


def semantic_limitations(text_rows: list[dict[str, Any]], skipped: bool) -> list[str]:
    limitations = []
    if skipped:
        limitations.append(
            "A rodada do subagent Codex da Q3 ainda nao foi integrada nesta geracao."
        )
    failed = [
        row
        for row in text_rows
        if row.get("extraction_status") not in {"ok"} and row.get("extraction_status")
    ]
    if failed:
        limitations.append(
            f"{len(failed)} documento(s) da subamostra nao tiveram texto extraivel para Q3."
        )
    return limitations


def merge_semantic_metrics(metrics_path: Path, semantic_metrics: dict[str, Any]) -> None:
    metrics = read_json(metrics_path)
    if not isinstance(metrics, dict):
        raise ValueError(f"Expected object in {metrics_path}")
    metrics["semantic_quality"] = semantic_metrics
    write_json(metrics_path, metrics)


def count_status(rows: Iterable[dict[str, Any]], status: str) -> int:
    return sum(1 for row in rows if row.get("status") == status)


def count_values(rows: Iterable[dict[str, Any]], field: str) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        value = row.get(field)
        if value is not None:
            counts[str(value)] += 1
    return dict(sorted(counts.items()))


def average_scores(row: dict[str, Any]) -> float | None:
    values = [float(row[field]) for field in SCORE_FIELDS if isinstance(row.get(field), int)]
    return round(sum(values) / len(values), 2) if values else None


def bounded_score(value: Any) -> int:
    if not isinstance(value, int):
        raise ValueError(f"Semantic score must be int, got {value!r}")
    if value < 0 or value > 4:
        raise ValueError(f"Semantic score out of range 0..4: {value}")
    return value


def as_str_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def optional_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def unique_strings(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(stable_json(row) + "\n" for row in rows),
        encoding="utf-8",
    )


def stable_json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()
