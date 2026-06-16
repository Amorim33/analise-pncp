from __future__ import annotations

import csv
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from pncp_analysis.config import AnalysisConfig, load_config
from pncp_analysis.utils import (
    format_display_date,
    format_display_date_range,
    format_percent,
    markdown_table,
    read_json,
)
from pncp_analysis.workflow import DEFAULT_CONFIG_PATH, PROCESSED_DIR, RAW_DIR, REPO_ROOT

REPORT_DIR = REPO_ROOT / "report"
REPORT_OUTPUT_DIR = REPORT_DIR / "output"
DEFAULT_PAPER_CONFIG_PATH = REPO_ROOT / "config" / "paper.yaml"
PAPER_MARKDOWN_PATH = REPORT_DIR / "relatorio-final.md"
PAPER_TEX_PATH = REPORT_OUTPUT_DIR / "relatorio-final.tex"
PAPER_PDF_PATH = REPORT_OUTPUT_DIR / "relatorio-final.pdf"
REFERENCES_PATH = REPORT_DIR / "references.bib"
APA_CSL_PATH = REPORT_DIR / "apa.csl"
TEMPLATE_PATH = REPORT_DIR / "template.tex"
REPOSITORY_URL = "https://github.com/Amorim33/analise-pncp"

PLACEHOLDER_PREFIX = "PREENCHER"


@dataclass(frozen=True)
class PaperConfig:
    mode: str
    title: str
    subtitle: str
    authors: list[str]
    course: str
    instructor: str
    institution: str
    date: str
    ai_disclosure: str


@dataclass(frozen=True)
class PaperPaths:
    markdown: Path
    tex: Path
    pdf: Path | None


PandocRunner = Callable[[Path, Path], None]


def load_paper_config(path: Path = DEFAULT_PAPER_CONFIG_PATH) -> PaperConfig:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"Invalid paper config file: {path}")
    return PaperConfig(
        mode=str(raw["mode"]),
        title=str(raw["title"]),
        subtitle=str(raw.get("subtitle", "")),
        authors=[str(author) for author in raw["authors"]],
        course=str(raw["course"]),
        instructor=str(raw["instructor"]),
        institution=str(raw["institution"]),
        date=str(raw["date"]),
        ai_disclosure=str(raw["ai_disclosure"]),
    )


def generate_paper(
    *,
    analysis_config_path: Path = DEFAULT_CONFIG_PATH,
    paper_config_path: Path = DEFAULT_PAPER_CONFIG_PATH,
    tex_only: bool = False,
    allow_placeholders: bool = False,
    tex_runner: PandocRunner | None = None,
    pdf_runner: PandocRunner | None = None,
    metrics_path: Path = PROCESSED_DIR / "metrics.json",
    sample_path: Path = PROCESSED_DIR / "sample.csv",
    collection_metadata_path: Path = RAW_DIR / "collection_metadata.json",
    pipeline_metadata_path: Path = PROCESSED_DIR / "pipeline_metadata.json",
    markdown_path: Path = PAPER_MARKDOWN_PATH,
    tex_path: Path = PAPER_TEX_PATH,
    pdf_path: Path = PAPER_PDF_PATH,
) -> PaperPaths:
    analysis_config = load_config(analysis_config_path)
    paper_config = load_paper_config(paper_config_path)
    validate_paper_config(paper_config, allow_placeholders=allow_placeholders)

    metrics = read_json(metrics_path)
    sample_rows = read_sample_rows(sample_path)
    collection_metadata = read_json(collection_metadata_path)
    if not isinstance(metrics, dict) or not isinstance(collection_metadata, dict):
        raise ValueError("metrics.json and collection_metadata.json must contain objects")
    pipeline_metadata = (
        read_json(pipeline_metadata_path) if pipeline_metadata_path.exists() else {}
    )
    if not isinstance(pipeline_metadata, dict):
        raise ValueError("pipeline_metadata.json must contain an object")

    tex_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown = render_paper_markdown(
        analysis_config=analysis_config,
        paper_config=paper_config,
        metrics=metrics,
        sample_rows=sample_rows,
        collection_metadata=collection_metadata,
        pipeline_metadata=pipeline_metadata,
    )
    markdown_path.write_text(markdown, encoding="utf-8")

    resolved_tex_runner = tex_runner or run_pandoc_tex
    resolved_pdf_runner = pdf_runner or run_pandoc_pdf
    resolved_tex_runner(markdown_path, tex_path)
    generated_pdf_path: Path | None = None
    if not tex_only:
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        resolved_pdf_runner(markdown_path, pdf_path)
        generated_pdf_path = pdf_path
    return PaperPaths(markdown=markdown_path, tex=tex_path, pdf=generated_pdf_path)


def validate_paper_config(config: PaperConfig, *, allow_placeholders: bool) -> None:
    if config.mode not in {"draft", "final"}:
        raise ValueError("config/paper.yaml mode must be 'draft' or 'final'")
    if config.mode == "final" and has_placeholders(config) and not allow_placeholders:
        raise ValueError(
            "config/paper.yaml is in final mode but still contains placeholders. "
            "Fill metadata or rerun with --allow-placeholders."
        )


def has_placeholders(config: PaperConfig) -> bool:
    values = [
        config.title,
        config.subtitle,
        *config.authors,
        config.course,
        config.instructor,
        config.institution,
        config.date,
    ]
    return any(value.strip().upper().startswith(PLACEHOLDER_PREFIX) for value in values)


def render_paper_markdown(
    *,
    analysis_config: AnalysisConfig,
    paper_config: PaperConfig,
    metrics: dict[str, Any],
    sample_rows: list[dict[str, str]],
    collection_metadata: dict[str, Any],
    pipeline_metadata: dict[str, Any] | None = None,
) -> str:
    pipeline_metadata = pipeline_metadata or {}
    city_metrics = require_list(metrics, "city_metrics")
    field_completeness = require_list(metrics, "field_completeness")
    document_stats = require_list(metrics, "document_stats")
    additional_findings = require_list(metrics, "additional_findings")
    api_examples = require_list(metrics, "api_examples")
    completeness_examples = metrics.get("completeness_examples", [])
    api_experiment = metrics.get("api_experiment", {})
    sp_fragmentation = metrics.get("sao_paulo_fragmentation_evidence", {})
    if not isinstance(sp_fragmentation, dict):
        sp_fragmentation = {}
    date_range = format_display_date_range(analysis_config.start_date, analysis_config.end_date)

    parts = [
        "---",
        f'title: "{paper_config.title}"',
        f'subtitle: "{paper_config.subtitle}"',
        "author:",
        *[f'  - "{author}"' for author in paper_config.authors],
        f'date: "{format_display_date(paper_config.date)}"',
        "lang: pt-BR",
        f'course: "{paper_config.course}"',
        f'instructor: "{paper_config.instructor}"',
        f'institution: "{paper_config.institution}"',
        (
            'abstract: "Relatório acadêmico exploratório sobre transparência, '
            "reutilização de dados e fragmentação institucional em contratações "
            'públicas municipais publicadas no PNCP."'
        ),
        "---",
        "",
        "# Introdução",
        "",
        (
            "Este trabalho analisa o Portal Nacional de Contratações Públicas (PNCP) "
            "como infraestrutura de governo aberto nas capitais do Sudeste brasileiro. "
            "A investigação foi organizada em duas questões de pesquisa:"
        ),
        "",
        (
            "Q1. Há completude nos dados fornecidos pelo PNCP nas prefeituras das "
            "capitais dos estados do sudeste brasileiro (São Paulo, Rio de Janeiro, "
            "Belo Horizonte e Vitória)?"
        ),
        "",
        "Q2. Os dados das APIs do PNCP são facilmente consumíveis?",
        "",
        (
            "O tema dialoga com a disciplina Governo Aberto porque combina acesso à "
            "informação, padrões tecnológicos, dados abertos e accountability. A própria "
            "disciplina orienta que o trabalho articule problema, objetivos, método e "
            "conclusões, com atenção à estrutura textual e às normas de citação "
            "[@curso2026]. O PNCP é especialmente relevante porque a Lei nº 14.133/2021 "
            "o institui como ambiente nacional de divulgação de contratações públicas "
            "[@lei14133]."
        ),
        "",
        (
            "O argumento central é que o PNCP amplia a transparência formal ao centralizar "
            "metadados, documentos e links de origem, mas a efetividade como governo "
            "aberto depende da completude dos registros e da capacidade de reconstituir "
            "a organização administrativa de cada prefeitura. O caso de São Paulo mostra "
            "essa tensão com mais nitidez: grande parte dos registros municipais aparece "
            "fora do CNPJ matriz do município."
        ),
        "",
        "# Objetivos e método",
        "",
        (
            "O objetivo geral é avaliar, de forma exploratória, como o PNCP expressa "
            "princípios de governo aberto nas contratações das capitais do Sudeste. A "
            "pesquisa combina análise documental e computacional: coleta registros por "
            "API, transforma os dados em snapshots auditáveis, calcula métricas e gera "
            "relatórios reprodutíveis."
        ),
        "",
        (
            "O recorte empírico considera pregões eletrônicos, modalidade 6 no PNCP, "
            f"publicados entre {date_range}. Foram usados os CNPJs matriz de Rio de "
            "Janeiro, Belo Horizonte e Vitória. Para São Paulo, combinou-se o CNPJ "
            "matriz com varredura por UF e código IBGE, filtrando entidades municipais "
            "executivas."
        ),
        "",
        render_collection_table(collection_metadata),
        "",
        (
            "A amostra principal inclui todos os registros elegíveis no período, após "
            "deduplicação por `numeroControlePNCP`. Para a análise de documentos, foi "
            "usada subamostra determinística de até "
            f"{analysis_config.document_sample_n} registros por capital. A semente "
            f"usada foi {analysis_config.seed}."
        ),
        "",
        (
            "As métricas de Q1 medem a presença de campos essenciais, como objeto, "
            "valores, datas, unidade, link de origem e documentos. As métricas de Q2 "
            "registram duração do experimento, tempo médio de resposta e falhas "
            "observadas durante o consumo da API."
        ),
        "",
        render_repository_reference(),
        "",
        (
            "O processo foi assistido pelo Codex como agente de programação e "
            "documentação, sob supervisão humana. A divisão agêntica usou as skills "
            "locais em `.agents/skills/`: mapeamento da API, coleta de dados, "
            "metodologia de amostragem e redação do relatório. As decisões "
            "substantivas, a validação das fontes e a interpretação final permanecem "
            "sob responsabilidade do autor; a declaração de uso de IA está no "
            "Apêndice B."
        ),
        "",
        "# Referencial teórico",
        "",
        (
            "Governo aberto costuma ser descrito como um arranjo que combina "
            "transparência, participação social, colaboração e prestação de contas. A "
            "Open Government Partnership associa o tema a compromissos de abertura, "
            "integridade pública e participação cidadã [@ogpDeclaration]. A OCDE também "
            "define governo aberto como uma cultura de governança que promove princípios "
            "de transparência, integridade, accountability e participação das partes "
            "interessadas [@oecd2017]."
        ),
        "",
        (
            "Dados abertos são uma dimensão operacional desse debate. Para que a "
            "publicação seja útil, não basta disponibilizar informação em páginas "
            "isoladas: é necessário permitir acesso, reuso, padronização e combinação "
            "com outras bases [@w3cManualDadosAbertos]. A Lei de Acesso à Informação "
            "também reforça a publicidade como regra e o sigilo como exceção "
            "[@lei12527]. Assim, transparência pública deve ser avaliada não apenas pela "
            "existência de dados, mas por sua usabilidade para fiscalização e pesquisa."
        ),
        "",
        (
            "No caso brasileiro, o PNCP constitui uma infraestrutura relevante para esse "
            "tipo de análise, pois centraliza informações e documentos de contratações "
            "públicas [@pncpPortal]. A existência de API e de dados consultáveis amplia "
            "o potencial de reutilização por cidadãos, pesquisadores e jornalistas "
            "[@pncpDadosAbertos; @pncpApiConsulta]."
        ),
        "",
        "# Desenvolvimento e análise",
        "",
        "## Visão comparativa",
        "",
        render_city_metrics_table(city_metrics),
        "",
        (
            "A primeira diferença relevante está na concentração institucional. Rio de "
            "Janeiro, Belo Horizonte e Vitória aparecem concentradas no CNPJ matriz no "
            "recorte adotado. São Paulo, por outro lado, apresenta múltiplos CNPJs "
            "municipais executivos associados a unidades como fundo municipal, hospital, "
            "companhia de engenharia de tráfego, secretaria e subprefeitura."
        ),
        "",
        "## Fragmentação em São Paulo",
        "",
        render_sp_fragmentation_table(sp_fragmentation),
        "",
        (
            "Esse resultado é substantivo para governo aberto. Uma consulta limitada ao "
            "CNPJ matriz de São Paulo recuperaria apenas uma fração dos registros "
            "elegíveis. Portanto, a transparência formal do PNCP convive com uma barreira "
            "de reconstrução institucional: o cidadão precisa saber que a prefeitura pode "
            "publicar contratações por diferentes CNPJs municipais."
        ),
        "",
        "## Q1: completude dos dados",
        "",
        render_completeness_matrix(field_completeness),
        "",
        (
            "A resposta a Q1 é positiva para os campos estruturantes do registro, mas "
            "com ressalvas relevantes. Nos registros elegíveis, objeto, valor estimado, "
            "datas básicas e unidade administrativa tiveram alta disponibilidade. A "
            "variação concentrou-se em valor homologado, link do sistema de origem e "
            "documentos, que foram avaliados na subamostra documental. Essa diferença "
            "importa para controle social porque a ausência de resultado homologado ou "
            "de link externo dificulta a reconstituição completa do processo."
        ),
        "",
        "Exemplos pseudoaleatórios da subamostra documental ilustram essa variação:",
        "",
        render_completeness_examples(completeness_examples),
        "",
        render_document_stats_table(document_stats),
        "",
        "## Q2: consumo da API",
        "",
        render_api_performance_table(collection_metadata, api_experiment, pipeline_metadata),
        "",
        (
            "A resposta a Q2 é intermediária. A API é consumível por scripts, retorna "
            "JSON estruturado e expõe paginação, mas o consumo não é trivial em uma "
            "janela anual: foi necessário dividir consultas em blocos mensais, respeitar "
            "pausas entre requisições e tratar limite de taxa. A duração total do "
            "experimento inclui coleta de contratações, geração da amostra e consulta "
            "a documentos da subamostra."
        ),
        "",
        render_api_error_notes(collection_metadata, api_experiment, pipeline_metadata),
        "",
        "## Constatações empíricas",
        "",
        render_bullets([str(item) for item in additional_findings]),
        "",
        "# Conclusões",
        "",
        (
            "A análise indica que o PNCP é uma infraestrutura importante de governo "
            "aberto: ele centraliza registros, expõe campos padronizados, oferece "
            "documentos e permite automação por API. Esses elementos fortalecem a "
            "transparência formal e criam condições para controle social."
        ),
        "",
        (
            "Ao mesmo tempo, a comparação mostra que abertura não é sinônimo automático "
            "de inteligibilidade. A fragmentação de CNPJs em São Paulo torna a busca "
            "mais complexa e pode subestimar a atividade contratual municipal quando o "
            "pesquisador consulta apenas o CNPJ matriz. A contribuição do trabalho está "
            "em mostrar que a avaliação de governo aberto deve observar também a "
            "arquitetura institucional dos dados."
        ),
        "",
        (
            "Como conclusão regional exploratória, as capitais do Sudeste analisadas "
            "apresentam boa disponibilidade básica de dados e documentos no PNCP, mas "
            "diferem na forma de organização dos registros. A agenda de melhoria passa "
            "por documentação mais clara dos CNPJs/unidades, maior completude de links "
            "de origem e mecanismos que facilitem ao cidadão reconstruir o universo de "
            "órgãos vinculados a cada prefeitura."
        ),
        "",
        "# Referências",
        "",
        "::: {#refs}",
        ":::",
        "",
        "\\appendix",
        "",
        "# Apêndice A: exemplos compactos da API",
        "",
        render_api_examples(api_examples[:4]),
        "",
        "# Apêndice B: declaração de uso de IA",
        "",
        paper_config.ai_disclosure,
        "",
        "# Apêndice C: limitações metodológicas",
        "",
        (
            "A pesquisa é exploratória e não representa todos os municípios do Sudeste. "
            "A API de consulta por publicação limita cada requisição a janelas de até "
            "365 dias; por isso, o recorte usa a maior janela aceita em uma consulta "
            "reprodutível. Além disso, documentos vinculados foram analisados por "
            "subamostra determinística, e os resultados podem mudar com novas "
            "publicações, retificações ou alterações na API do PNCP."
        ),
        "",
    ]
    return "\n".join(parts)


def render_collection_table(collection_metadata: dict[str, Any]) -> str:
    sources = collection_metadata.get("sources", [])
    rows = []
    if isinstance(sources, list):
        for source in sources:
            if isinstance(source, dict):
                rows.append(
                    [
                        source.get("city", ""),
                        format_source_kind(str(source.get("kind", ""))),
                        source.get("records", 0),
                        source.get("pages_collected", ""),
                        source.get("total_pages", ""),
                        format_collection_limit(source),
                    ]
                )
    return markdown_table(
        ["Capital", "Fonte", "Registros", "Páginas", "Total", "Limite"],
        rows,
    )


def render_repository_reference() -> str:
    return (
        "A reprodutibilidade foi organizada no repositório GitHub "
        f"<{REPOSITORY_URL}>. O repositório versiona código Python, configurações, "
        "snapshots brutos, tabelas processadas, métricas, análise exploratória e o "
        "relatório final em Markdown, LaTeX e PDF, na branch `main`."
    )


def format_source_kind(kind: str) -> str:
    if kind == "matrix_cnpj":
        return "matriz"
    if kind == "municipality_scan":
        return "município"
    return kind


def format_collection_limit(source: dict[str, Any]) -> str:
    if source.get("kind") == "municipality_scan" and source.get("max_pages") is None:
        return "todas"
    value = source.get("max_pages")
    return "" if value is None else str(value)


def render_city_metrics_table(city_metrics: list[dict[str, Any]]) -> str:
    return markdown_table(
        [
            "Capital",
            "Candidatos",
            "Amostra",
            "CNPJs distintos",
            "Registros na matriz",
            "Participação da matriz",
        ],
        [
            [
                item.get("city", ""),
                item.get("candidate_count", 0),
                item.get("sample_count", 0),
                item.get("distinct_cnpj_count", 0),
                item.get("matrix_records", 0),
                format_percent(as_optional_float(item.get("matrix_share"))),
            ]
            for item in city_metrics
        ],
    )


def render_sp_fragmentation_table(fragmentation: dict[str, Any]) -> str:
    return markdown_table(
        ["Métrica", "Valor"],
        [
            ["CNPJ matriz", fragmentation.get("matrix_cnpj", "")],
            ["Registros candidatos", fragmentation.get("candidate_count", 0)],
            ["Registros no CNPJ matriz", fragmentation.get("matrix_records", 0)],
            ["Registros fora do CNPJ matriz", fragmentation.get("outside_matrix_records", 0)],
            [
                "Participação fora da matriz",
                format_percent(as_optional_float(fragmentation.get("outside_matrix_share"))),
            ],
            ["CNPJs distintos", fragmentation.get("distinct_cnpj_count", 0)],
            ["CNPJs fora da matriz", fragmentation.get("outside_matrix_cnpj_count", 0)],
        ],
    )


def render_completeness_summary(field_completeness: list[dict[str, Any]]) -> str:
    selected_fields = {"Valor homologado", "Link de origem", "Documentos"}
    rows = [
        [
            item.get("city", ""),
            item.get("field", ""),
            item.get("present", 0),
            item.get("sample_count", 0),
            format_percent(as_optional_float(item.get("share"))),
        ]
        for item in field_completeness
        if item.get("field") in selected_fields
    ]
    return markdown_table(["Capital", "Campo", "Presentes", "Amostra", "Percentual"], rows)


def render_completeness_matrix(field_completeness: list[dict[str, Any]]) -> str:
    fields = [
        ("Obj.", "Objeto"),
        ("Estim.", "Valor estimado"),
        ("Homol.", "Valor homologado"),
        ("Data", "Data de publicacao"),
        ("Unid.", "Unidade"),
        ("Link", "Link de origem"),
        ("Docs", "Documentos"),
    ]
    cities = []
    for item in field_completeness:
        city = item.get("city")
        if city not in cities:
            cities.append(city)

    rows = []
    for city in cities:
        rows.append(
            [
                city,
                *[
                    format_percent(find_completeness_share(field_completeness, city, field))
                    for _, field in fields
                ],
            ]
        )
    return markdown_table(["Capital", *[label for label, _ in fields]], rows)


def render_completeness_examples(examples: Any) -> str:
    if not isinstance(examples, list) or not examples:
        return "- Nenhum exemplo sorteado foi registrado."

    lines = []
    for item in examples:
        if not isinstance(item, dict):
            continue
        lines.append(
            f"- {item.get('city', '')} (`{item.get('numeroControlePNCP', '')}`): "
            f"data {format_display_date(str(item.get('dataPublicacaoPncp') or ''))}; "
            f"valor homologado {presence_label(item.get('valorTotalHomologado'))}; "
            f"link de origem {presence_label(item.get('linkSistemaOrigem'))}; "
            f"{item.get('document_count', 0)} documento(s); objeto: "
            f"{truncate(str(item.get('objetoCompra') or ''), 150)}"
        )
    return "\n".join(lines)


def find_completeness_share(
    field_completeness: list[dict[str, Any]],
    city: Any,
    field: str,
) -> float | None:
    for item in field_completeness:
        if item.get("city") == city and item.get("field") == field:
            return as_optional_float(item.get("share"))
    return None


def render_document_stats_table(document_stats: list[dict[str, Any]]) -> str:
    rows = []
    for item in document_stats:
        rows.append(
            [
                item.get("city", ""),
                item.get("records_with_documents", 0),
                item.get("sample_count", 0),
                item.get("min_documents", 0),
                item.get("max_documents", 0),
                f"{float(item.get('avg_documents') or 0):.1f}",
            ]
        )
    return markdown_table(
        ["Capital", "Com documentos", "Amostra", "Mín.", "Máx.", "Média"],
        rows,
    )


def render_api_performance_table(
    collection_metadata: dict[str, Any],
    api_experiment: Any,
    pipeline_metadata: dict[str, Any],
) -> str:
    collection_perf = collection_metadata.get("api_performance", {})
    if not isinstance(collection_perf, dict):
        collection_perf = {}
    document_perf = {}
    if isinstance(api_experiment, dict) and isinstance(
        api_experiment.get("document_api_performance"),
        dict,
    ):
        document_perf = api_experiment["document_api_performance"]

    collection_duration = optional_float(collection_metadata.get("duration_seconds"))
    document_duration = (
        optional_float(api_experiment.get("duration_seconds"))
        if isinstance(api_experiment, dict)
        else None
    )
    pipeline_duration = optional_float(pipeline_metadata.get("duration_seconds"))
    if pipeline_duration is None:
        pipeline_duration = sum(
            value for value in [collection_duration, document_duration] if value
        )

    attempt = pipeline_metadata.get("collection_attempt", {})
    attempt_failed = isinstance(attempt, dict) and attempt.get("status") == "failed"
    rows = [
        performance_row(
            "Snapshots" if attempt_failed else "Contratações",
            collection_perf,
            collection_duration,
        ),
    ]
    if attempt_failed:
        attempt_perf = attempt.get("api_performance", {})
        rows.append(
            performance_row(
                "Tentativa live",
                attempt_perf if isinstance(attempt_perf, dict) else {},
                optional_float(attempt.get("duration_seconds")),
            )
        )
    rows.extend(
        [
            performance_row("Documentos", document_perf, document_duration),
            ["Total", "", "", "", format_seconds(pipeline_duration), ""],
        ]
    )

    return markdown_table(
        ["Etapa", "Req.", "Sucesso", "Média", "Duração", "Falhas"],
        rows,
    )


def performance_row(label: str, performance: dict[str, Any], duration: float | None) -> list[Any]:
    return [
        label,
        performance.get("request_count", "n/a"),
        performance.get("successful_request_count", "n/a"),
        format_seconds(optional_float(performance.get("average_success_response_seconds"))),
        format_seconds(duration),
        performance.get("failed_attempt_count", "n/a"),
    ]


def render_api_error_notes(
    collection_metadata: dict[str, Any],
    api_experiment: Any,
    pipeline_metadata: dict[str, Any],
) -> str:
    collection_failures = collection_metadata.get("failures", [])
    collection_failure_count = (
        len(collection_failures) if isinstance(collection_failures, list) else 0
    )
    document_failures = []
    observed_errors = []
    if isinstance(api_experiment, dict):
        raw_document_failures = api_experiment.get("document_api_failures", [])
        if isinstance(raw_document_failures, list):
            document_failures = raw_document_failures
        raw_observed = api_experiment.get("observed_experiment_errors", [])
        if isinstance(raw_observed, list):
            observed_errors = [str(item) for item in raw_observed]

    attempt = pipeline_metadata.get("collection_attempt", {})
    attempt_failed = isinstance(attempt, dict) and attempt.get("status") == "failed"
    if attempt_failed:
        lines = [
            (
                "Os snapshots de coleta reutilizados registravam "
                f"{collection_failure_count} falha(s) persistente(s) na coleta "
                "bem-sucedida anterior. Na execução final, a consulta de documentos "
                f"registrou {len(document_failures)} falha(s) persistente(s)."
            )
        ]
        lines.append(
            "A tentativa live desta execução falhou e o pipeline reutilizou snapshots "
            f"existentes. Erro registrado: {truncate(str(attempt.get('error') or ''), 220)}"
        )
    else:
        lines = [
            (
                f"Na execução final, a coleta registrou {collection_failure_count} "
                "falha(s) persistente(s) e a consulta de documentos registrou "
                f"{len(document_failures)}."
            )
        ]
    if observed_errors:
        lines.append(
            "Durante a experimentação, apareceram estes problemas: "
            + "; ".join(observed_errors)
        )
    return "\n\n".join(lines)


def render_api_examples(api_examples: list[Any]) -> str:
    blocks = []
    for example in api_examples:
        if not isinstance(example, dict):
            continue
        payload = example.get("payload", {})
        if not isinstance(payload, dict):
            continue
        orgao = payload.get("orgaoEntidade", {})
        unidade = payload.get("unidadeOrgao", {})
        docs = payload.get("documentos", [])
        orgao_cnpj = orgao.get("cnpj", "") if isinstance(orgao, dict) else ""
        orgao_nome = orgao.get("razaoSocial", "") if isinstance(orgao, dict) else ""
        unidade_nome = unidade.get("nomeUnidade", "") if isinstance(unidade, dict) else ""
        blocks.extend(
            [
                f"## {example.get('label', 'Exemplo')}",
                "",
                f"- Controle PNCP: `{payload.get('numeroControlePNCP', '')}`",
                f"- CNPJ/órgão: `{orgao_cnpj}` — {orgao_nome}",
                f"- Unidade: {unidade_nome}",
                f"- Valor estimado: {format_value(payload.get('valorTotalEstimado'))}",
                f"- Valor homologado: {format_value(payload.get('valorTotalHomologado'))}",
                f"- Situação: {format_value(payload.get('situacaoCompraNome'))}",
                f"- Documentos listados no exemplo: {len(docs) if isinstance(docs, list) else 0}",
                f"- Objeto: {truncate(str(payload.get('objetoCompra') or ''), 260)}",
                "",
            ]
        )
    return "\n".join(blocks)


def render_bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def read_sample_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def require_list(payload: dict[str, Any], key: str) -> list[Any]:
    value = payload.get(key)
    if not isinstance(value, list):
        raise ValueError(f"metrics.json field {key!r} must be a list")
    return value


def as_optional_float(value: Any) -> float | None:
    return optional_float(value)


def truncate(value: str, max_length: int) -> str:
    clean = " ".join(value.replace("\\n", " ").replace("\\r", " ").split())
    if len(clean) <= max_length:
        return clean
    return clean[: max_length - 3] + "..."


def format_value(value: Any) -> str:
    if value is None:
        return "não informado"
    if isinstance(value, str) and not value.strip():
        return "não informado"
    return str(value)


def presence_label(value: Any) -> str:
    if value is None:
        return "ausente"
    if isinstance(value, str) and not value.strip():
        return "ausente"
    if isinstance(value, list) and not value:
        return "ausente"
    return "presente"


def optional_float(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    return None


def format_seconds(value: float | None) -> str:
    if value is None:
        return "n/a"
    if value < 60:
        return f"{value:.2f}s"
    minutes, seconds = divmod(value, 60)
    if minutes < 60:
        return f"{int(minutes)}min {seconds:.1f}s"
    hours, remainder = divmod(minutes, 60)
    return f"{int(hours)}h {int(remainder)}min {seconds:.0f}s"


def run_pandoc_tex(markdown_path: Path, output_path: Path) -> None:
    run_pandoc(markdown_path, output_path)


def run_pandoc_pdf(markdown_path: Path, output_path: Path) -> None:
    run_pandoc(markdown_path, output_path)


def run_pandoc(markdown_path: Path, output_path: Path) -> None:
    command = [
        "pandoc",
        str(markdown_path),
        "--from",
        "markdown+yaml_metadata_block+raw_tex",
        "--citeproc",
        "--csl",
        str(APA_CSL_PATH),
        "--bibliography",
        str(REFERENCES_PATH),
        "--template",
        str(TEMPLATE_PATH),
        "--pdf-engine",
        "xelatex",
        "--syntax-highlighting=none",
        "-o",
        str(output_path),
    ]
    subprocess.run(command, check=True, cwd=REPO_ROOT)
