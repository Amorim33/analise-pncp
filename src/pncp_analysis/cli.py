from __future__ import annotations

import argparse
from pathlib import Path

from pncp_analysis import paper, workflow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pncp-analysis",
        description="Analise exploratoria do PNCP nas capitais do Sudeste.",
    )
    parser.add_argument(
        "--config",
        default=str(workflow.DEFAULT_CONFIG_PATH),
        help="Caminho para config/analysis.yaml.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    collect_parser = subparsers.add_parser("collect", help="Coleta snapshots da API PNCP.")
    collect_parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limita registros por consulta. Util para smoke tests live.",
    )
    collect_parser.add_argument(
        "--live",
        action="store_true",
        help="Alias documentado para testes de integracao; a coleta ja e live.",
    )

    subparsers.add_parser("sample", help="Monta amostra deterministica.")

    analyze_parser = subparsers.add_parser("analyze", help="Calcula metricas da amostra.")
    analyze_parser.add_argument(
        "--skip-documents",
        action="store_true",
        help="Nao consulta metadados de documentos vinculados.",
    )

    subparsers.add_parser("report", help="Gera analise-exploratoria.md.")

    paper_parser = subparsers.add_parser("paper", help="Gera relatorio final em LaTeX/PDF.")
    paper_parser.add_argument(
        "--paper-config",
        default=str(paper.DEFAULT_PAPER_CONFIG_PATH),
        help="Caminho para config/paper.yaml.",
    )
    paper_parser.add_argument(
        "--tex-only",
        action="store_true",
        help="Gera somente paper/output/relatorio-final.tex.",
    )
    paper_parser.add_argument(
        "--allow-placeholders",
        action="store_true",
        help="Permite compilar com metadados placeholder em modo final.",
    )

    subparsers.add_parser("run-all", help="Executa coleta, amostra, analise e relatorio.")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    config_path = Path(args.config)

    if args.command == "collect":
        workflow.collect(config_path=config_path, limit=args.limit)
    elif args.command == "sample":
        workflow.sample(config_path=config_path)
    elif args.command == "analyze":
        workflow.analyze(config_path=config_path, skip_documents=args.skip_documents)
    elif args.command == "report":
        workflow.report(config_path=config_path)
    elif args.command == "paper":
        paper.generate_paper(
            analysis_config_path=config_path,
            paper_config_path=Path(args.paper_config),
            tex_only=args.tex_only,
            allow_placeholders=args.allow_placeholders,
        )
    elif args.command == "run-all":
        workflow.run_all(config_path=config_path)
    else:
        parser.error(f"Unknown command: {args.command}")
