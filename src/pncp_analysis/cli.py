from __future__ import annotations

import argparse
from pathlib import Path

from pncp_analysis import workflow


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

    semantic_parser = subparsers.add_parser(
        "semantic",
        help="Prepara a avaliacao semantica Q3 para o subagent Codex.",
    )
    semantic_parser.add_argument(
        "--skip-gpt",
        action="store_true",
        help="Alias legado: gera selecao, textos e inputs da Q3 para o subagent Codex.",
    )
    semantic_parser.add_argument(
        "--reuse-existing",
        action="store_true",
        help="Reusa q3_semantic_metrics.json existente e injeta em metrics.json.",
    )
    semantic_parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limita a quantidade de contratos avaliados. Util para smoke tests.",
    )

    subparsers.add_parser("report", help="Gera analise-exploratoria.md.")

    run_all_parser = subparsers.add_parser(
        "run-all",
        help="Executa coleta, amostra, analise, Q3 semantica e relatorio.",
    )
    run_all_parser.add_argument(
        "--skip-q3",
        action="store_true",
        help="Nao executa a etapa semantica Q3.",
    )

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
    elif args.command == "semantic":
        workflow.semantic(
            config_path=config_path,
            skip_gpt=args.skip_gpt,
            reuse_existing=args.reuse_existing,
            limit=args.limit,
        )
    elif args.command == "report":
        workflow.report(config_path=config_path)
    elif args.command == "run-all":
        workflow.run_all(config_path=config_path, skip_q3=args.skip_q3)
    else:
        parser.error(f"Unknown command: {args.command}")
