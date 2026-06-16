from __future__ import annotations

import argparse
import sys
import time
import traceback
from collections.abc import Callable
from pathlib import Path
from typing import Any

from pncp_analysis import paper, workflow
from pncp_analysis.config import load_config
from pncp_analysis.utils import read_json, utc_now_iso, write_json

EVENTS_PATH = workflow.PROCESSED_DIR / "script_execution_events.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Refaz a coleta PNCP e reconstrói a narrativa de Q2 com telemetria "
            "por request."
        )
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=workflow.DEFAULT_CONFIG_PATH,
        help="Caminho para config/analysis.yaml.",
    )
    parser.add_argument(
        "--paper-config",
        type=Path,
        default=paper.DEFAULT_PAPER_CONFIG_PATH,
        help="Caminho para config/paper.yaml.",
    )
    parser.add_argument(
        "--allow-placeholders",
        action="store_true",
        help="Permite metadados placeholder caso config/paper.yaml esteja em modo final.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    workflow.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    events: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    run_started_at = utc_now_iso()
    run_started = time.perf_counter()
    status = "complete"
    finished = False

    def persist() -> None:
        run_status = "complete" if finished and status == "complete" else status
        if not finished and status == "complete":
            run_status = "running"
        finished_at = utc_now_iso()
        duration_seconds = round(time.perf_counter() - run_started, 3)
        write_json(
            EVENTS_PATH,
            {
                "source": "scripts/rebuild_q2.py",
                "generated_at": finished_at,
                "started_at": run_started_at,
                "finished_at": finished_at,
                "duration_seconds": duration_seconds,
                "status": run_status,
                "events": events,
                "errors": errors,
            },
        )
        write_json(
            workflow.PROCESSED_DIR / "pipeline_metadata.json",
            {
                "source": "scripts/rebuild_q2.py",
                "started_at": run_started_at,
                "finished_at": finished_at,
                "duration_seconds": duration_seconds,
                "steps": [
                    "collect",
                    "sample",
                    "analyze",
                    "report",
                    "paper_markdown",
                ],
                "collection_status": "complete" if run_status == "complete" else run_status,
                "collection_attempt": {},
                "status": run_status,
            },
        )

    def run_step(name: str, command: str, action: Callable[[], None]) -> None:
        nonlocal status
        started_at = utc_now_iso()
        started = time.perf_counter()
        event: dict[str, Any] = {
            "name": name,
            "command": command,
            "started_at": started_at,
            "note": "",
        }
        try:
            action()
        except Exception as exc:
            status = "failed"
            event["name"] = f"failed_{name}"
            event["exit_code"] = 1
            event["error"] = str(exc)
            errors.append(
                {
                    "step": name,
                    "command": command,
                    "error": str(exc),
                    "traceback": traceback.format_exc(),
                }
            )
            raise
        finally:
            event["finished_at"] = utc_now_iso()
            event["duration_seconds"] = round(time.perf_counter() - started, 3)
            event.setdefault("exit_code", 0)
            events.append(event)
            persist()

    try:
        run_step(
            "main_successful_collection",
            f"uv run pncp-analysis --config {args.config} collect",
            lambda: workflow.collect(config_path=args.config),
        )
        run_step(
            "q2_sample_generation",
            f"uv run pncp-analysis --config {args.config} sample",
            lambda: workflow.sample(config_path=args.config),
        )
        run_step(
            "q2_document_analysis",
            f"uv run pncp-analysis --config {args.config} analyze",
            lambda: workflow.analyze(config_path=args.config),
        )
        run_step(
            "final_report_generation",
            f"uv run pncp-analysis --config {args.config} report",
            lambda: workflow.report(config_path=args.config),
        )
        run_step(
            "q2_paper_markdown_generation",
            "uv run python scripts/rebuild_q2.py # render report/relatorio-final.md",
            lambda: write_paper_markdown(
                analysis_config_path=args.config,
                paper_config_path=args.paper_config,
                allow_placeholders=args.allow_placeholders,
            ),
        )
        finished = True
        persist()
        workflow.report(config_path=args.config)
        write_paper_markdown(
            analysis_config_path=args.config,
            paper_config_path=args.paper_config,
            allow_placeholders=args.allow_placeholders,
        )
    except Exception:
        persist()
        raise


def write_paper_markdown(
    *,
    analysis_config_path: Path,
    paper_config_path: Path,
    allow_placeholders: bool,
) -> None:
    analysis_config = load_config(analysis_config_path)
    paper_config = paper.load_paper_config(paper_config_path)
    paper.validate_paper_config(paper_config, allow_placeholders=allow_placeholders)

    metrics = read_json(workflow.PROCESSED_DIR / "metrics.json")
    collection_metadata = read_json(workflow.RAW_DIR / "collection_metadata.json")
    if not isinstance(metrics, dict) or not isinstance(collection_metadata, dict):
        raise ValueError("metrics.json and collection_metadata.json must contain objects")
    metrics["script_execution_events"] = read_json(EVENTS_PATH)

    pipeline_metadata = (
        read_json(workflow.PROCESSED_DIR / "pipeline_metadata.json")
        if (workflow.PROCESSED_DIR / "pipeline_metadata.json").exists()
        else {}
    )
    if not isinstance(pipeline_metadata, dict):
        raise ValueError("pipeline_metadata.json must contain an object")

    sample_rows = paper.read_sample_rows(workflow.PROCESSED_DIR / "sample.csv")
    markdown = paper.render_paper_markdown(
        analysis_config=analysis_config,
        paper_config=paper_config,
        metrics=metrics,
        sample_rows=sample_rows,
        collection_metadata=collection_metadata,
        pipeline_metadata=pipeline_metadata,
    )
    paper.PAPER_MARKDOWN_PATH.parent.mkdir(parents=True, exist_ok=True)
    paper.PAPER_MARKDOWN_PATH.write_text(markdown, encoding="utf-8")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
