"""Q4. Avaliacao de objeto + documentos via `claude` CLI.

Avalia uma subamostra de contratacoes do PNCP em tres aspectos praticos de controle
social, usando julgamento real de um LLM atraves do `claude` CLI (assinatura logada):

1. clareza_objeto         -- e facil entender o que foi contratado?
2. compatibilidade_preco  -- o preco parece compativel com o objeto contratado?
3. consumibilidade_documento -- o documento e facil de consumir? PDF escaneado vs texto.

O aspecto 3 usa um sinal deterministico (chars/pagina, paginas com texto) calculado
localmente a partir dos PDFs em cache, passado ao modelo como verdade-base.

Saidas:
  data/processed/q4_document_quality_evaluations.jsonl
  data/processed/q4_document_quality_metrics.json
"""

from __future__ import annotations

import argparse
import json
import re
import signal
import subprocess
import time
import zipfile
from collections import Counter, defaultdict
from io import BytesIO
from pathlib import Path
from typing import Any

from pncp_analysis.config import AnalysisConfig, load_config
from pncp_analysis.semantic import (
    SCORE_FIELDS as _Q3_SCORE_FIELDS,  # noqa: F401 - referencia de paridade Q3
)
from pncp_analysis.semantic import (
    compact_record,
    normalize_extracted_text,
    select_primary_document,
    sha256_text,
    stable_json,
    unique_strings,
    utc_now_iso,
)
from pncp_analysis.utils import read_json, write_json

ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
CONFIG_PATH = ROOT / "config" / "analysis.yaml"

DOCUMENT_SAMPLE_PATH = DATA_PROCESSED / "document_sample.json"
DOCUMENT_INDEX_PATH = DATA_RAW / "sample_documents.json"
EVAL_OUTPUT_PATH = DATA_PROCESSED / "q4_document_quality_evaluations.jsonl"
METRICS_OUTPUT_PATH = DATA_PROCESSED / "q4_document_quality_metrics.json"

PROMPT_VERSION = "q4-doc-quality-v1"
SCHEMA_VERSION = "q4-doc-quality-schema-v1"
DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_LIMIT = 20

ASPECTS = ["clareza_objeto", "compatibilidade_preco", "consumibilidade_documento"]

# Heuristica de camada de texto do PDF (chars por pagina).
TEXT_PAGE_THRESHOLD = 200
SCANNED_PAGE_THRESHOLD = 50
PDF_EXTRACTION_TIMEOUT_SECONDS = 8
CLI_TIMEOUT_SECONDS = 180

SYSTEM_PROMPT = (
    "Voce e um avaliador de transparencia em contratacoes publicas (PNCP), voltado a "
    "controle social. Avalie SOMENTE com base no registro da API e no texto/metadados "
    "do documento principal fornecidos. Nao use conhecimento externo nem busque na web. "
    "Para o aspecto de PDF escaneado vs. texto, trate o sinal deterministico fornecido "
    "(chars_por_pagina, paginas_com_texto, rotulo_heuristico) como verdade-base. "
    "Responda EXCLUSIVAMENTE com um unico objeto JSON valido, sem markdown, sem "
    "comentarios, sem texto fora do JSON."
)


# --------------------------------------------------------------------------------------
# Extracao de texto + sinal deterministico de "escaneado"
# --------------------------------------------------------------------------------------


class _Timeout(Exception):
    pass


def _alarm_handler(signum: int, frame: Any) -> None:  # noqa: ARG001
    raise _Timeout("PDF extraction timed out.")


def extract_pdf_stats(body: bytes) -> dict[str, Any]:
    """Extrai texto e estatisticas por pagina de um PDF (com timeout)."""
    from pypdf import PdfReader

    previous = signal.signal(signal.SIGALRM, _alarm_handler)
    signal.alarm(PDF_EXTRACTION_TIMEOUT_SECONDS)
    try:
        reader = PdfReader(BytesIO(body))
        page_texts = [page.extract_text() or "" for page in reader.pages]
    except _Timeout:
        return {"paginas": 0, "chars_total": 0, "paginas_com_texto": 0, "text": "",
                "error": "pdf_timeout"}
    except Exception as exc:  # noqa: BLE001 - registra falha por documento
        return {"paginas": 0, "chars_total": 0, "paginas_com_texto": 0, "text": "",
                "error": str(exc)}
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous)

    text = normalize_extracted_text("\n".join(page_texts))
    return {
        "paginas": len(page_texts),
        "chars_total": len(text),
        "paginas_com_texto": sum(1 for t in page_texts if t.strip()),
        "text": text,
        "error": None,
    }


def analyze_document_bytes(filename: str, body: bytes) -> dict[str, Any]:
    """Devolve sinal deterministico + texto para um documento (pdf, zip, docx, texto)."""
    suffix = Path(filename.lower()).suffix
    is_pdf = suffix == ".pdf" or body.startswith(b"%PDF")
    is_zip = suffix == ".zip" or (not is_pdf and zipfile.is_zipfile(BytesIO(body)))

    if is_pdf:
        stats = extract_pdf_stats(body)
        return _finalize_stats("pdf", [stats], errors=_errs(stats))

    if is_zip:
        pdf_stats: list[dict[str, Any]] = []
        text_chunks: list[str] = []
        errors: list[str] = []
        try:
            with zipfile.ZipFile(BytesIO(body)) as archive:
                for member in sorted(archive.namelist()):
                    if member.endswith("/") or member.startswith("__MACOSX/"):
                        continue
                    msuffix = Path(member.lower()).suffix
                    payload = archive.read(member)
                    if msuffix == ".pdf" or payload.startswith(b"%PDF"):
                        stats = extract_pdf_stats(payload)
                        pdf_stats.append(stats)
                        if stats["text"]:
                            text_chunks.append(f"--- {member} ---\n{stats['text']}")
                        errors.extend(_errs(stats, prefix=member))
                    elif msuffix in {".txt", ".csv", ".html", ".htm"}:
                        decoded = normalize_extracted_text(
                            payload.decode("utf-8", errors="replace")
                        )
                        if decoded:
                            text_chunks.append(f"--- {member} ---\n{decoded}")
        except Exception as exc:  # noqa: BLE001
            return _finalize_stats("zip", [], errors=[str(exc)], text="")
        joined = normalize_extracted_text("\n\n".join(text_chunks))
        return _finalize_stats("zip", pdf_stats, errors=errors, text=joined)

    if suffix in {".docx"}:
        try:
            from docx import Document

            document = Document(BytesIO(body))
            text = normalize_extracted_text(
                "\n".join(p.text for p in document.paragraphs)
            )
        except Exception as exc:  # noqa: BLE001
            return _finalize_stats("docx", [], errors=[str(exc)], text="")
        return _finalize_stats("docx", [], errors=[], text=text, force_label="texto")

    if suffix in {".txt", ".csv", ".html", ".htm"}:
        text = normalize_extracted_text(body.decode("utf-8", errors="replace"))
        return _finalize_stats(suffix.lstrip("."), [], errors=[], text=text,
                               force_label="texto")

    return _finalize_stats(suffix.lstrip(".") or "unknown", [], errors=[], text="")


def _errs(stats: dict[str, Any], prefix: str | None = None) -> list[str]:
    if not stats.get("error"):
        return []
    return [f"{prefix}: {stats['error']}" if prefix else str(stats["error"])]


def _finalize_stats(
    file_type: str,
    pdf_stats: list[dict[str, Any]],
    *,
    errors: list[str],
    text: str | None = None,
    force_label: str | None = None,
) -> dict[str, Any]:
    paginas = sum(s["paginas"] for s in pdf_stats)
    chars_total = sum(s["chars_total"] for s in pdf_stats)
    paginas_com_texto = sum(s["paginas_com_texto"] for s in pdf_stats)
    if text is None:
        text = normalize_extracted_text(
            "\n\n".join(s["text"] for s in pdf_stats if s["text"])
        )
    if text and not chars_total:
        # documentos baseados em texto (docx/txt/html) sem contagem por pagina
        chars_total = len(text)

    chars_por_pagina = round(chars_total / paginas, 1) if paginas else float(chars_total)

    if force_label:
        rotulo = force_label
    elif chars_total == 0:
        rotulo = "sem_texto"
    elif paginas and chars_por_pagina < SCANNED_PAGE_THRESHOLD:
        rotulo = "escaneado"
    elif paginas and chars_por_pagina < TEXT_PAGE_THRESHOLD:
        rotulo = "misto"
    else:
        rotulo = "texto"

    return {
        "file_type": file_type,
        "paginas": paginas,
        "chars_total": chars_total,
        "chars_por_pagina": chars_por_pagina,
        "paginas_com_texto": paginas_com_texto,
        "rotulo_heuristico": rotulo,
        "text": text,
        "errors": unique_strings(errors)[:5],
    }


# --------------------------------------------------------------------------------------
# Leitura do cache de documentos (sem rede)
# --------------------------------------------------------------------------------------


def read_cached_binary(cache_dir: Path, url: str) -> tuple[str, bytes] | None:
    digest = sha256_text(url)[:16]
    matches = sorted(cache_dir.glob(f"{digest}_*"))
    if not matches:
        return None
    path = matches[0]
    filename = path.name.split("_", 1)[1] if "_" in path.name else path.name
    return filename, path.read_bytes()


# --------------------------------------------------------------------------------------
# Prompt + invocacao do claude CLI
# --------------------------------------------------------------------------------------


def build_user_prompt(
    *, api_record: dict[str, Any], doc_meta: dict[str, Any], signal_block: dict[str, Any],
    text_excerpt: str,
) -> str:
    schema_hint = (
        '{\n'
        '  "clareza_objeto": {"nota": 0-4, "justificativa": "uma frase curta"},\n'
        '  "compatibilidade_preco": {"nota": 0-4, '
        '"sinal": "compativel|incerto|suspeito", "justificativa": "uma frase curta"},\n'
        '  "consumibilidade_documento": {"nota": 0-4, '
        '"tipo_pdf": "texto|escaneado|misto|sem_texto|sem_documento", '
        '"justificativa": "uma frase curta"},\n'
        '  "resumo": "uma frase",\n'
        '  "alertas": ["..."]\n'
        '}'
    )
    return (
        "Avalie esta contratacao em tres aspectos, com nota inteira de 0 a 4 "
        "(0=pessimo, 4=otimo).\n\n"
        "ASPECTOS:\n"
        "1. clareza_objeto -- E facil entender O QUE foi contratado a partir do objeto e "
        "das informacoes do registro? Penalize objetos genericos/curtos (ex.: "
        '"aquisicao", "prestacao de servicos") e jargao sem escopo.\n'
        "2. compatibilidade_preco -- O valor (valorTotalEstimado / valorTotalHomologado) "
        "parece compativel com o objeto contratado e com a modalidade? Sinalize valores "
        "ausentes, zerados, ou aparentemente desproporcionais ao objeto. Use \"incerto\" "
        "quando nao houver base suficiente -- nao invente preco de mercado.\n"
        "3. consumibilidade_documento -- O documento principal e facil de consumir? Use o "
        "sinal deterministico fornecido: PDF com camada de texto pesquisavel (facil) vs. "
        "PDF escaneado/imagem sem texto (dificil para controle social). Considere tambem "
        "ausencia de documento.\n\n"
        f"REGISTRO_API:\n{stable_json(api_record)}\n\n"
        f"DOCUMENTO_PRINCIPAL (metadados):\n{stable_json(doc_meta)}\n\n"
        f"SINAL_DETERMINISTICO_PDF (verdade-base para o aspecto 3):\n"
        f"{stable_json(signal_block)}\n\n"
        f"TEXTO_DOCUMENTO (excerto):\n{text_excerpt or '(indisponivel)'}\n\n"
        f"Responda APENAS com este JSON:\n{schema_hint}"
    )


def strip_fences(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```[a-zA-Z]*\n?", "", stripped)
        stripped = re.sub(r"\n?```$", "", stripped.strip())
    return stripped.strip()


def call_claude(model: str, user_prompt: str) -> dict[str, Any]:
    proc = subprocess.run(
        [
            "claude", "-p",
            "--model", model,
            "--output-format", "json",
            "--append-system-prompt", SYSTEM_PROMPT,
            "--max-turns", "1",
            "--allowedTools", "",
        ],
        input=user_prompt,
        text=True,
        capture_output=True,
        timeout=CLI_TIMEOUT_SECONDS,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"claude CLI falhou (rc={proc.returncode}): {proc.stderr[:400]}")
    envelope: dict[str, Any] = json.loads(proc.stdout)
    if envelope.get("is_error"):
        raise RuntimeError(f"claude CLI is_error: {str(envelope.get('result'))[:300]}")
    return envelope


# --------------------------------------------------------------------------------------
# Normalizacao da avaliacao
# --------------------------------------------------------------------------------------


def bounded(value: Any) -> int | None:
    try:
        return max(0, min(4, int(value)))
    except (TypeError, ValueError):
        return None


def normalize_evaluation(answer: dict[str, Any]) -> dict[str, Any]:
    def block(name: str) -> dict[str, Any]:
        value = answer.get(name)
        return value if isinstance(value, dict) else {}

    def aspect(name: str, *extra: str) -> dict[str, Any]:
        raw = block(name)
        out: dict[str, Any] = {
            "nota": bounded(raw.get("nota")),
            "justificativa": str(raw.get("justificativa") or ""),
        }
        for key in extra:
            out[key] = str(raw.get(key) or "")
        return out

    clareza = aspect("clareza_objeto")
    preco = aspect("compatibilidade_preco", "sinal")
    consumo = aspect("consumibilidade_documento", "tipo_pdf")
    notas = [a["nota"] for a in (clareza, preco, consumo) if isinstance(a["nota"], int)]
    return {
        "clareza_objeto": clareza,
        "compatibilidade_preco": preco,
        "consumibilidade_documento": consumo,
        "resumo": str(answer.get("resumo") or ""),
        "alertas": [str(item) for item in answer.get("alertas", [])][:10]
        if isinstance(answer.get("alertas"), list)
        else [],
        "nota_media": round(sum(notas) / len(notas), 2) if notas else None,
    }


# --------------------------------------------------------------------------------------
# Loop principal
# --------------------------------------------------------------------------------------


def select_subsample(records: list[dict[str, Any]], limit: int | None) -> list[dict[str, Any]]:
    ordered = sorted(records, key=lambda r: str(r.get("numeroControlePNCP") or ""))
    return ordered if limit is None else ordered[:limit]


def evaluate_record(
    *,
    record: dict[str, Any],
    doc_index: dict[str, Any],
    cache_dir: Path,
    config: AnalysisConfig,
    model: str,
) -> dict[str, Any]:
    control = str(record.get("numeroControlePNCP") or "")
    city = record.get("_analysisCity")
    docs = doc_index.get(control, [])
    docs_list = [d for d in docs if isinstance(d, dict)] if isinstance(docs, list) else []
    selection = select_primary_document(control, docs_list)
    selected = selection.get("selected_document")

    base_row: dict[str, Any] = {
        "numeroControlePNCP": control,
        "city": city,
        "prompt_version": PROMPT_VERSION,
        "schema_version": SCHEMA_VERSION,
        "model": model,
        "available_documents": selection.get("available_documents"),
        "selection_reason": selection.get("selection_reason"),
    }

    if not isinstance(selected, dict):
        base_row.update({"status": "no_document", "pdf_signal": None})
        return base_row

    url = str(selected.get("url") or selected.get("uri") or "")
    cached = read_cached_binary(cache_dir, url) if url else None
    if cached is None:
        base_row.update({"status": "no_cached_document", "document_url": url,
                         "pdf_signal": None})
        return base_row

    filename, body = cached
    analysis = analyze_document_bytes(filename, body)
    pdf_signal = {k: analysis[k] for k in (
        "file_type", "paginas", "chars_total", "chars_por_pagina",
        "paginas_com_texto", "rotulo_heuristico", "errors")}

    doc_meta = {
        "titulo": selected.get("titulo"),
        "tipo": selected.get("tipoDocumentoNome") or selected.get("tipoDocumentoDescricao"),
        "file_type": analysis["file_type"],
        "document_url": url,
    }
    user_prompt = build_user_prompt(
        api_record=compact_record(record),
        doc_meta=doc_meta,
        signal_block=pdf_signal,
        text_excerpt=analysis["text"][: config.semantic.max_document_chars],
    )

    base_row.update({"document_url": url, "pdf_signal": pdf_signal})
    try:
        envelope = call_claude(model, user_prompt)
    except Exception as exc:  # noqa: BLE001 - falha por registro nao aborta o lote
        base_row.update({"status": "cli_error", "error": str(exc)[:400]})
        return base_row

    base_row["cli_usage"] = {
        "total_cost_usd": envelope.get("total_cost_usd"),
        "usage": envelope.get("usage"),
        "duration_ms": envelope.get("duration_ms"),
        "stop_reason": envelope.get("stop_reason"),
    }
    try:
        answer = json.loads(strip_fences(str(envelope.get("result") or "")))
    except json.JSONDecodeError as exc:
        base_row.update({"status": "parse_error", "error": str(exc),
                         "raw_result": str(envelope.get("result"))[:1000]})
        return base_row

    base_row.update({"status": "evaluated", **normalize_evaluation(answer)})
    return base_row


def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    evaluated = [r for r in rows if r.get("status") == "evaluated"]

    def avg_aspect(subset: list[dict[str, Any]], aspect: str) -> float | None:
        notas = [
            r[aspect]["nota"] for r in subset
            if isinstance(r.get(aspect), dict) and isinstance(r[aspect].get("nota"), int)
        ]
        return round(sum(notas) / len(notas), 2) if notas else None

    def block(subset: list[dict[str, Any]]) -> dict[str, Any]:
        medias = [r["nota_media"] for r in subset if isinstance(r.get("nota_media"), (int, float))]
        return {
            "count": len(subset),
            **{f"avg_{a}": avg_aspect(subset, a) for a in ASPECTS},
            "avg_nota_media": round(sum(medias) / len(medias), 2) if medias else None,
        }

    by_city: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in evaluated:
        by_city[str(row.get("city") or "")].append(row)

    tipo_pdf = Counter(
        r["consumibilidade_documento"].get("tipo_pdf")
        for r in evaluated
        if isinstance(r.get("consumibilidade_documento"), dict)
    )
    rotulo_heuristico = Counter(
        r["pdf_signal"]["rotulo_heuristico"]
        for r in rows
        if isinstance(r.get("pdf_signal"), dict)
    )
    sinal_preco = Counter(
        r["compatibilidade_preco"].get("sinal")
        for r in evaluated
        if isinstance(r.get("compatibilidade_preco"), dict)
    )

    total_cost = sum(
        float(r["cli_usage"]["total_cost_usd"])
        for r in rows
        if isinstance(r.get("cli_usage"), dict) and r["cli_usage"].get("total_cost_usd")
    )

    examples = [
        {
            "numeroControlePNCP": r.get("numeroControlePNCP"),
            "city": r.get("city"),
            "nota_media": r.get("nota_media"),
            "resumo": r.get("resumo"),
            "alertas": r.get("alertas", [])[:4],
            "tipo_pdf": r.get("consumibilidade_documento", {}).get("tipo_pdf"),
        }
        for r in sorted(
            evaluated,
            key=lambda r: (0 if r.get("alertas") else 1, r.get("nota_media") or 99),
        )[:8]
    ]

    return {
        "generated_at": utc_now_iso(),
        "question": "Q4. O objeto e o preco sao claros e os documentos faceis de consumir?",
        "model": rows[0]["model"] if rows else DEFAULT_MODEL,
        "prompt_version": PROMPT_VERSION,
        "schema_version": SCHEMA_VERSION,
        "sample_count": len(rows),
        "evaluated_count": len(evaluated),
        "status_counts": dict(sorted(Counter(str(r.get("status")) for r in rows).items())),
        "overall": block(evaluated),
        "by_city": [
            {"city": city, **block(subset)}
            for city, subset in sorted(by_city.items())
            if city
        ],
        "tipo_pdf_counts": dict(sorted((str(k), v) for k, v in tipo_pdf.items())),
        "rotulo_heuristico_counts": dict(sorted((str(k), v) for k, v in rotulo_heuristico.items())),
        "sinal_preco_counts": dict(sorted((str(k), v) for k, v in sinal_preco.items())),
        "examples": examples,
        "cost": {"total_cost_usd": round(total_cost, 4)},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT,
                        help="Numero de registros a avaliar (default 20; 0 = todos).")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--delay", type=float, default=0.5,
                        help="Pausa em segundos entre chamadas do CLI.")
    args = parser.parse_args()

    config = load_config(CONFIG_PATH)
    cache_dir = Path(config.semantic.document_cache_dir)
    if not cache_dir.is_absolute():
        cache_dir = ROOT / cache_dir

    records = read_json(DOCUMENT_SAMPLE_PATH)
    doc_index = read_json(DOCUMENT_INDEX_PATH)
    if not isinstance(records, list) or not isinstance(doc_index, dict):
        raise ValueError("document_sample.json deve ser lista e sample_documents.json objeto")

    limit = None if args.limit == 0 else args.limit
    subsample = select_subsample(
        [r for r in records if isinstance(r, dict)], limit
    )

    rows: list[dict[str, Any]] = []
    for index, record in enumerate(subsample, start=1):
        row = evaluate_record(
            record=record,
            doc_index=doc_index,
            cache_dir=cache_dir,
            config=config,
            model=args.model,
        )
        rows.append(row)
        print(
            f"[{index}/{len(subsample)}] {row.get('numeroControlePNCP')} "
            f"status={row.get('status')} nota_media={row.get('nota_media')}",
            flush=True,
        )
        if args.delay and index < len(subsample):
            time.sleep(args.delay)

    EVAL_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVAL_OUTPUT_PATH.write_text(
        "".join(stable_json(row) + "\n" for row in rows), encoding="utf-8"
    )
    metrics = aggregate(rows)
    write_json(METRICS_OUTPUT_PATH, metrics)

    print(stable_json({
        "evaluated_count": metrics["evaluated_count"],
        "status_counts": metrics["status_counts"],
        "overall": metrics["overall"],
        "tipo_pdf_counts": metrics["tipo_pdf_counts"],
        "total_cost_usd": metrics["cost"]["total_cost_usd"],
    }))


if __name__ == "__main__":
    main()
