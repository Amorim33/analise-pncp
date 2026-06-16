from __future__ import annotations

import json
from typing import Any

from pncp_analysis.api_events import (
    ApiExperimentEvidence,
    build_api_experiment_evidence,
    estimated_total_seconds,
    format_local_datetime,
    format_optional_int,
)
from pncp_analysis.config import AnalysisConfig
from pncp_analysis.utils import (
    format_display_date,
    format_display_date_range,
    format_percent,
    markdown_table,
)

REPOSITORY_URL = "https://github.com/Amorim33/analise-pncp"


def render_report(
    config: AnalysisConfig,
    metrics: dict[str, Any],
    sampled: list[dict[str, Any]],
    collection_metadata: dict[str, Any] | None = None,
    pipeline_metadata: dict[str, Any] | None = None,
) -> str:
    collection_metadata = collection_metadata or {}
    pipeline_metadata = pipeline_metadata or {}
    city_metrics = metrics.get("city_metrics", [])
    field_completeness = metrics.get("field_completeness", [])
    top_sp = metrics.get("sao_paulo_top_cnpjs", [])
    sp_fragmentation = metrics.get("sao_paulo_fragmentation_evidence", {})
    sample_rows = metrics.get("sample_rows", [])
    api_examples = metrics.get("api_examples", [])
    completeness_examples = metrics.get("completeness_examples", [])
    additional_findings = metrics.get("additional_findings", [])
    document_stats = metrics.get("document_stats", [])
    limitations = metrics.get("limitations", [])
    sample = metrics.get("sample", {})
    document_sample = metrics.get("document_sample", {})
    api_experiment = metrics.get("api_experiment", {})
    script_execution_events = metrics.get("script_execution_events", {})
    date_range = format_display_date_range(config.start_date, config.end_date)

    parts = [
        "# Analise exploratoria do PNCP nas capitais do Sudeste",
        "",
        "## Resumo",
        "",
        (
            "Esta analise compara contratacoes de Pregao Eletronico publicadas no PNCP "
            f"entre {date_range} pelas capitais do Sudeste. "
            "O desenho e exploratorio: ele busca avaliar transparencia, completude dos "
            "dados e fragmentacao institucional, sem pretender representar todos os "
            "municipios da regiao."
        ),
        "",
        (
            "O metodo combina coleta por **API**^[**API**: interface de programacao de "
            "aplicacoes; neste trabalho, e o meio automatizado de consulta aos dados "
            "do PNCP.], analise de completude e medicao de consumibilidade dos "
            "endpoints. O processo foi apoiado pelo **Codex**^[**Codex**: agente de "
            "programacao e documentacao usado para implementar, validar e revisar o "
            "pipeline.] e organizado por **skills**^[**Skills**: "
            "instrucoes locais que especializam agentes para tarefas como mapear a "
            "**API**, coletar dados, revisar amostragem e redigir o relatorio.]."
        ),
        "",
        "O principal achado metodologico e que Sao Paulo aparece de forma fragmentada: "
        "a consulta apenas pelo CNPJ matriz subrepresenta o municipio, enquanto a busca "
        "por codigo IBGE revela varios CNPJs municipais executivos.",
        "",
        "## Questoes de pesquisa",
        "",
        (
            "- Q1. Ha completude nos dados fornecidos pelo PNCP nas prefeituras das "
            "capitais dos estados do Sudeste brasileiro (Sao Paulo, Rio de Janeiro, "
            "Belo Horizonte e Vitoria)?"
        ),
        (
            "- Q2. Os dados das **APIs** do PNCP sao facilmente consumiveis?"
        ),
        "",
        "## Metodologia",
        "",
        markdown_table(
            ["Parametro", "Valor"],
            [
                ["Periodo", date_range],
                ["Modalidade", f"{config.modality_name} ({config.modality_id})"],
                ["Amostra principal", describe_analysis_sample(config, sample)],
                ["Amostra documental", describe_document_sample(config, document_sample)],
                ["Seed", config.seed],
            ],
        ),
        "",
        "Para Rio de Janeiro, Belo Horizonte e Vitoria, a coleta usou o CNPJ matriz do "
        "municipio. Para Sao Paulo, a coleta combinou o CNPJ matriz com uma busca por "
        "UF e codigo IBGE, filtrando orgaos municipais executivos e excluindo orgaos "
        "legislativos como a Camara Municipal.",
        "",
        "## Reprodutibilidade e processo agentico",
        "",
        (
            f"O repositorio GitHub <{REPOSITORY_URL}> versiona o codigo Python, "
            "configuracoes, snapshots brutos, tabelas processadas, metricas, analise "
            "exploratoria e relatorio final. O processo foi assistido pelo **Codex** como "
            "agente de programacao e documentacao, sob supervisao humana."
        ),
        "",
        (
            "A divisao agentica foi registrada em **skills** locais no caminho "
            "`.agents/skills/`, com papeis para mapeamento da **API**, coleta de dados, "
            "metodologia de amostragem e redacao do relatorio. "
            "As decisoes substantivas, validacao de fontes e interpretacao final "
            "permanecem sob responsabilidade do autor."
        ),
        "",
        "## Exemplos de registros retornados pela API",
        "",
        (
            "Os exemplos abaixo usam um subconjunto dos campos retornados pela API do PNCP. "
            "Eles mostram como a informacao chega para a analise: identificador PNCP, orgao, "
            "unidade, objeto, valores, situacao, link de origem e documentos vinculados."
        ),
        "",
        render_api_examples(api_examples),
        "",
        "## Amostra",
        "",
        render_city_metrics_table(city_metrics),
        "",
        (
            "A amostra principal inclui todos os registros elegiveis no periodo, apos "
            "deduplicacao por `numeroControlePNCP`. Para documentos vinculados, o "
            "pipeline usa uma subamostra deterministica de ate "
            f"{config.document_sample_n} registros por capital, tambem ordenada e "
            "sorteada com seed reprodutivel."
        ),
        "",
        "## Resultados",
        "",
        render_sample_table(sample_rows),
        "",
        "## Constatações adicionais",
        "",
        render_findings(additional_findings),
        "",
        "## Fragmentacao de CNPJs em Sao Paulo",
        "",
        render_sp_fragmentation_summary(sp_fragmentation),
        "",
        "A tabela abaixo mostra os principais CNPJs municipais encontrados no recorte de "
        "Sao Paulo apos o filtro de orgaos executivos municipais.",
        "",
        render_sp_top_table(top_sp),
        "",
        "Exemplos de registros fora do CNPJ matriz reforcam que a fragmentacao nao e "
        "apenas nominal: diferentes CNPJs publicam objetos e unidades administrativas "
        "proprias no PNCP.",
        "",
        render_sp_non_matrix_examples(sp_fragmentation),
        "",
        "Esse resultado sugere que a transparencia via PNCP nao depende apenas da "
        "existencia do portal, mas tambem da forma como a administracao estrutura e "
        "publica seus registros. Uma busca pelo CNPJ matriz de Sao Paulo tende a perder "
        "contratacoes relevantes de secretarias, fundos, empresas e unidades municipais.",
        "",
        "## Completude dos dados",
        "",
        (
            "Para Q1, a completude foi avaliada campo a campo na amostra principal, "
            "que contem todos os registros elegiveis. Objeto, valor estimado, datas "
            "basicas e unidade administrativa aparecem como campos de alta "
            "disponibilidade; as maiores fragilidades estao em valor homologado, link "
            "do sistema de origem e, no caso de documentos, na subamostra documental."
        ),
        "",
        render_completeness_matrix(field_completeness),
        "",
        "Exemplos sorteados de forma pseudoaleatoria, com seed fixa:",
        "",
        render_completeness_examples(completeness_examples),
        "",
        "Tabela completa de campos analisados:",
        "",
        render_completeness_table(field_completeness),
        "",
        "## Documentos vinculados",
        "",
        render_document_stats(document_stats),
        "",
        "A presenca de objeto, datas, valores, unidade administrativa e link de origem "
        "foi medida no universo elegivel. Documentos vinculados foram medidos na "
        "subamostra documental. Essas metricas nao avaliam a qualidade textual dos "
        "documentos, mas indicam se um cidadao ou pesquisador consegue localizar "
        "informacoes basicas para controle social.",
        "",
        "## Consumo da API",
        "",
        (
            "Para Q2, a coleta foi reexecutada com telemetria por request. Cada chamada "
            "preserva URL, status HTTP, tentativa, instante de inicio, instante de fim, "
            "duracao e erro observado. A leitura dos resultados indica consumibilidade "
            "tecnica real, mas nao trivial: os endpoints retornam dados estruturados e "
            "paginados, enquanto a execucao anual depende de blocos temporais, retries, "
            "pausas entre paginas e validacao de `Content-Type` para separar JSON valido "
            "de respostas HTML de bloqueio ou indisponibilidade."
        ),
        "",
        render_api_performance(collection_metadata, api_experiment, script_execution_events),
        "",
        render_api_session_event_summary(
            collection_metadata,
            api_experiment,
            script_execution_events,
        ),
        "",
        render_api_error_notes(
            collection_metadata,
            api_experiment,
            pipeline_metadata,
            script_execution_events,
        ),
        "",
        "## Limitacoes",
        "",
        render_limitations(limitations),
        "",
        "## Conclusao regional",
        "",
        (
            "O PNCP oferece uma infraestrutura relevante de governo aberto para as "
            "capitais do Sudeste, pois centraliza registros, padroniza campos e permite "
            "consulta por API. No entanto, a comparacao mostra que a abertura formal dos "
            "dados nao elimina assimetrias de acesso. A fragmentacao de CNPJs em Sao "
            "Paulo e um achado substantivo: mesmo com dados publicos, a capacidade de "
            "controle social depende de conhecer a organizacao administrativa por tras "
            "dos registros."
        ),
        "",
        (
            "Assim, a conclusao regional e que o PNCP fortalece a transparencia formal, "
            "mas sua efetividade como instrumento de governo aberto depende da "
            "completude documental, da padronizacao dos registros e da facilidade de "
            "reconstituir o universo institucional de cada prefeitura."
        ),
        "",
        "## Reproducibilidade",
        "",
        "```bash",
        "uv sync --extra dev",
        "uv run pncp-analysis run-all",
        "make check",
        "```",
        "",
        "## Referencias tecnicas",
        "",
        "- API de consulta PNCP: <https://pncp.gov.br/pncp-consulta/v3/api-docs>",
        "- API PNCP: <https://pncp.gov.br/pncp-api/v3/api-docs>",
        "- Modalidades PNCP: <https://pncp.gov.br/api/pncp/v1/modalidades>",
        "",
    ]
    return "\n".join(parts)


def render_api_examples(api_examples: Any) -> str:
    if not isinstance(api_examples, list) or not api_examples:
        return "_Nenhum exemplo registrado._"

    blocks = []
    for item in api_examples:
        if not isinstance(item, dict):
            continue
        label = item.get("label", "Exemplo")
        payload = item.get("payload", {})
        blocks.extend(
            [
                f"### {label}",
                "",
                "```json",
                json.dumps(payload, ensure_ascii=False, indent=2),
                "```",
            ]
        )
    return "\n".join(blocks)


def render_city_metrics_table(city_metrics: Any) -> str:
    rows = []
    if isinstance(city_metrics, list):
        for item in city_metrics:
            if isinstance(item, dict):
                rows.append(
                    [
                        item.get("city", ""),
                        item.get("candidate_count", 0),
                        item.get("sample_count", 0),
                        item.get("distinct_cnpj_count", 0),
                        item.get("matrix_records", 0),
                        format_percent(item.get("matrix_share")),
                    ]
                )
    return markdown_table(
        [
            "Capital",
            "Registros candidatos",
            "Amostra",
            "CNPJs distintos",
            "Registros no CNPJ matriz",
            "Participacao da matriz",
        ],
        rows,
    )


def render_sample_table(sample_rows: Any) -> str:
    rows = []
    if isinstance(sample_rows, list):
        for item in sample_rows[:25]:
            if isinstance(item, dict):
                rows.append(
                    [
                        item.get("city", ""),
                        item.get("numeroControlePNCP", ""),
                        item.get("cnpj", ""),
                        item.get("orgao", ""),
                        item.get("document_count", 0),
                    ]
                )
    table = markdown_table(["Capital", "Controle PNCP", "CNPJ", "Orgao", "Docs"], rows)
    if isinstance(sample_rows, list) and len(sample_rows) > len(rows):
        return (
            f"{table}\n\n"
            f"_Tabela limitada aos primeiros {len(rows)} registros de {len(sample_rows)} "
            "elegiveis para manter o relatorio legivel._"
        )
    return table


def render_findings(findings: Any) -> str:
    if not isinstance(findings, list) or not findings:
        return "- Nenhuma constatacao adicional registrada."
    return "\n".join(f"- {item}" for item in findings)


def render_sp_fragmentation_summary(sp_fragmentation: Any) -> str:
    if not isinstance(sp_fragmentation, dict) or not sp_fragmentation:
        return "_Sem evidencias de fragmentacao registradas._"

    return markdown_table(
        ["Metrica", "Valor"],
        [
            ["CNPJ matriz", sp_fragmentation.get("matrix_cnpj", "")],
            ["Registros candidatos de Sao Paulo", sp_fragmentation.get("candidate_count", 0)],
            ["Registros no CNPJ matriz", sp_fragmentation.get("matrix_records", 0)],
            ["Registros fora do CNPJ matriz", sp_fragmentation.get("outside_matrix_records", 0)],
            [
                "Participacao fora do CNPJ matriz",
                format_percent(sp_fragmentation.get("outside_matrix_share")),
            ],
            ["CNPJs distintos no recorte", sp_fragmentation.get("distinct_cnpj_count", 0)],
            [
                "CNPJs distintos fora da matriz",
                sp_fragmentation.get("outside_matrix_cnpj_count", 0),
            ],
        ],
    )


def render_sp_top_table(top_sp: Any) -> str:
    rows = []
    if isinstance(top_sp, list):
        for item in top_sp:
            if isinstance(item, dict):
                rows.append(
                    [
                        item.get("cnpj", ""),
                        item.get("razao_social", ""),
                        item.get("records", 0),
                    ]
                )
    return markdown_table(["CNPJ", "Razao social", "Registros"], rows)


def render_sp_non_matrix_examples(sp_fragmentation: Any) -> str:
    if not isinstance(sp_fragmentation, dict):
        return "_Sem exemplos registrados._"
    examples = sp_fragmentation.get("non_matrix_examples", [])
    if not isinstance(examples, list) or not examples:
        return "_Sem exemplos registrados._"

    rows = []
    for item in examples:
        if isinstance(item, dict):
            rows.append(
                [
                    item.get("cnpj", ""),
                    item.get("razao_social", ""),
                    item.get("example_control", ""),
                    item.get("example_unit", ""),
                    truncate(str(item.get("example_object") or ""), 120),
                ]
            )
    return markdown_table(["CNPJ", "Orgao", "Controle PNCP", "Unidade", "Objeto"], rows)


def render_completeness_table(field_completeness: Any) -> str:
    rows = []
    if isinstance(field_completeness, list):
        for item in field_completeness:
            if isinstance(item, dict):
                rows.append(
                    [
                        item.get("city", ""),
                        item.get("field", ""),
                        item.get("present", 0),
                        item.get("sample_count", 0),
                        format_percent(item.get("share")),
                    ]
                )
    return markdown_table(["Capital", "Campo", "Presentes", "Amostra", "Percentual"], rows)


def render_completeness_matrix(field_completeness: Any) -> str:
    fields = [
        "Objeto",
        "Valor estimado",
        "Valor homologado",
        "Data de publicacao",
        "Unidade",
        "Link de origem",
        "Documentos",
    ]
    cities = []
    if isinstance(field_completeness, list):
        for item in field_completeness:
            if isinstance(item, dict) and item.get("city") not in cities:
                cities.append(item.get("city"))

    rows = []
    for city in cities:
        rows.append(
            [
                city,
                *[
                    format_percent(find_completeness_share(field_completeness, city, field))
                    for field in fields
                ],
            ]
        )
    return markdown_table(["Capital", *fields], rows)


def render_completeness_examples(examples: Any) -> str:
    if not isinstance(examples, list) or not examples:
        return "- Nenhum exemplo de completude registrado."

    rows = []
    for item in examples:
        if isinstance(item, dict):
            rows.append(
                [
                    item.get("city", ""),
                    item.get("numeroControlePNCP", ""),
                    format_display_date(str(item.get("dataPublicacaoPncp") or "")),
                    presence_label(item.get("valorTotalHomologado")),
                    presence_label(item.get("linkSistemaOrigem")),
                    item.get("document_count", 0),
                    truncate(str(item.get("objetoCompra") or ""), 90),
                ]
            )
    return markdown_table(
        ["Capital", "Controle PNCP", "Data", "Valor homologado", "Link", "Docs", "Objeto"],
        rows,
    )


def find_completeness_share(field_completeness: Any, city: Any, field: str) -> float | None:
    if not isinstance(field_completeness, list):
        return None
    for item in field_completeness:
        if isinstance(item, dict) and item.get("city") == city and item.get("field") == field:
            value = item.get("share")
            return value if isinstance(value, float) else None
    return None


def render_document_stats(document_stats: Any) -> str:
    rows = []
    if isinstance(document_stats, list):
        for item in document_stats:
            if isinstance(item, dict):
                rows.append(
                    [
                        item.get("city", ""),
                        item.get("records_with_documents", 0),
                        item.get("sample_count", 0),
                        item.get("min_documents", 0),
                        item.get("max_documents", 0),
                        f"{float(item.get('avg_documents') or 0):.1f}",
                        ", ".join(item.get("document_types", [])[:5]),
                    ]
                )
    return markdown_table(
        [
            "Capital",
            "Com docs",
            "Amostra",
            "Min docs",
            "Max docs",
            "Media docs",
            "Tipos observados",
        ],
        rows,
    )


def render_api_performance(
    collection_metadata: dict[str, Any],
    api_experiment: Any,
    script_execution_events: Any,
) -> str:
    evidence = build_api_experiment_evidence(
        collection_metadata,
        api_experiment,
        script_execution_events,
    )
    total_seconds = estimated_total_seconds(evidence)
    rows: list[list[Any]] = [
        [
            "Coleta anual de contratações",
            (
                format_optional_int(evidence.collection_request_count)
                if evidence.collection_request_count is not None
                else evidence.collection_pages
            ),
            (
                format_optional_int(evidence.collection_successful_request_count)
                if evidence.collection_successful_request_count is not None
                else evidence.collection_pages
            ),
            format_seconds(evidence.collection_avg_seconds),
            format_seconds(evidence.collection_p95_seconds),
            format_seconds(evidence.collection_duration_seconds),
            format_optional_int(evidence.collection_failed_attempt_count),
        ],
        [
            "Consulta de documentos",
            format_optional_int(evidence.document_request_count),
            format_optional_int(evidence.document_successful_request_count),
            format_seconds(evidence.document_avg_seconds),
            format_seconds(evidence.document_p95_seconds),
            format_seconds(evidence.document_duration_seconds),
            format_optional_int(evidence.document_failed_attempt_count),
        ],
    ]
    if evidence.report_event:
        rows.append(
            [
                "Geração final do relatório",
                "n/a",
                "completa",
                "n/a",
                "n/a",
                format_seconds(evidence.report_event.duration_seconds),
                0,
            ]
        )
    rows.append(["Experimento observado", "", "", "", "", format_seconds(total_seconds), ""])
    return markdown_table(
        ["Etapa", "Requisições", "Sucessos", "Tempo médio", "P95", "Duração", "Falhas"],
        rows,
    )


def render_api_error_notes(
    collection_metadata: dict[str, Any],
    api_experiment: Any,
    pipeline_metadata: dict[str, Any],
    script_execution_events: Any,
) -> str:
    collection_failures = collection_metadata.get("failures", [])
    document_failures = []
    observed_errors = []
    if isinstance(api_experiment, dict):
        raw_document_failures = api_experiment.get("document_api_failures", [])
        if isinstance(raw_document_failures, list):
            document_failures = raw_document_failures
        raw_observed = api_experiment.get("observed_experiment_errors", [])
        if isinstance(raw_observed, list):
            observed_errors = [str(item) for item in raw_observed]

    evidence = build_api_experiment_evidence(
        collection_metadata,
        api_experiment,
        script_execution_events,
    )
    attempt = pipeline_metadata.get("collection_attempt", {})
    attempt_failed = isinstance(attempt, dict) and attempt.get("status") == "failed"
    collection_failure_count = (
        len(collection_failures) if isinstance(collection_failures, list) else 0
    )
    lines = [
        (
            "- Nos artefatos usados pela analise, a coleta anual completa registrou "
            f"{collection_failure_count} falhas de base ou pagina preservadas nos "
            "metadados; a paginacao final permaneceu completa apos retry ou fallback."
        ),
        (
            "- Na consulta documental, o script registrou "
            f"{len(document_failures)} falhas nao recuperadas."
        ),
    ]
    if evidence.collection_request_metrics_path and evidence.collection_errors_path:
        lines.append(
            "- A telemetria detalhada da coleta foi preservada em "
            f"`{evidence.collection_request_metrics_path}`; erros e tentativas "
            f"malsucedidas ficam em `{evidence.collection_errors_path}`."
        )
    if evidence.document_request_metrics_path and evidence.document_errors_path:
        lines.append(
            "- A telemetria detalhada da consulta documental foi preservada em "
            f"`{evidence.document_request_metrics_path}`; erros e tentativas "
            f"malsucedidas ficam em `{evidence.document_errors_path}`."
        )
    if evidence.timeout_probe_event:
        lines.append(
            "- Sondagens tecnicas da sessao apontaram instabilidade em paginas "
            "intermediarias: quatro de sete paginas testadas retornaram timeout de "
            "leitura de aproximadamente 15s."
        )
    if attempt_failed:
        lines.append(
            "- Uma execucao posterior de `run-all`, usada para revalidacao, falhou na "
            "coleta live com resposta HTTP 503 em HTML e reutilizou snapshots. Ela "
            "nao foi usada como duracao do experimento principal."
        )
    if evidence.fallback_event:
        lines.append(
            "- Essa revalidacao com fallback durou "
            f"{format_seconds(evidence.fallback_event.duration_seconds)}, separada da "
            "coleta completa usada na computacao."
        )
    lines.extend(f"- Durante a experimentação: {item}" for item in observed_errors)
    return "\n".join(lines)


def render_api_session_event_summary(
    collection_metadata: dict[str, Any],
    api_experiment: Any,
    script_execution_events: Any,
) -> str:
    evidence = build_api_experiment_evidence(
        collection_metadata,
        api_experiment,
        script_execution_events,
    )
    lines = [render_collection_script_summary(evidence)]
    document_summary = render_document_api_session_summary(evidence)
    if document_summary:
        lines.append(document_summary)
    return "\n".join(lines)


def render_collection_script_summary(evidence: ApiExperimentEvidence) -> str:
    if not evidence.collection_event:
        return (
            "- Historico de execucao: indisponivel nos artefatos processados; a tabela "
            "usa metricas internas do pipeline e os logs de request preservados."
        )
    final_note = ""
    if evidence.final_collection_event:
        final_note = (
            " Reexecucao posterior que materializou os snapshots finais: "
            f"{format_seconds(evidence.final_collection_event.duration_seconds)}."
        )
    return (
        "- Historico de execucao: a coleta completa usada na computacao foi "
        f"`{evidence.collection_event.command}`, iniciada em "
        f"{format_local_datetime(evidence.collection_event.started_at)} e concluida em "
        f"{format_local_datetime(evidence.collection_event.finished_at)}, com duracao "
        f"de {format_seconds(evidence.collection_event.duration_seconds)} e codigo "
        f"de saida {format_optional_int(evidence.collection_event.exit_code)}. A etapa "
        f"materializou {evidence.collection_records} registros brutos em "
        f"{evidence.collection_pages} paginas de resposta da API. As chamadas "
        f"bem-sucedidas tiveram media de {format_seconds(evidence.collection_avg_seconds)}, "
        f"p95 de {format_seconds(evidence.collection_p95_seconds)} e maximo de "
        f"{format_seconds(evidence.collection_max_seconds)}.{final_note}"
    )


def render_document_api_session_summary(evidence: ApiExperimentEvidence) -> str:
    if evidence.document_request_count is None:
        return ""
    return (
        "- Consulta documental: "
        f"{format_optional_int(evidence.document_successful_request_count)}/"
        f"{format_optional_int(evidence.document_request_count)} chamadas foram "
        "bem-sucedidas, com tempo medio de "
        f"{format_seconds(evidence.document_avg_seconds)}, p95 de "
        f"{format_seconds(evidence.document_p95_seconds)}, maximo de "
        f"{format_seconds(evidence.document_max_seconds)} e "
        f"{format_optional_int(evidence.document_failed_attempt_count)} tentativas "
        "malsucedidas. A API e consumivel, mas a execucao mostra que a resposta a Q2 "
        "deve considerar desempenho, erros preservados, validacao de payload e "
        "snapshots auditaveis, nao apenas a existencia formal do endpoint."
    )


def render_limitations(limitations: Any) -> str:
    if not isinstance(limitations, list):
        return "- Nenhuma limitacao registrada."
    return "\n".join(f"- {item}" for item in limitations)


def truncate(value: str, max_length: int) -> str:
    clean = " ".join(value.replace("\\n", " ").replace("\\r", " ").split())
    if len(clean) <= max_length:
        return clean
    return clean[: max_length - 3] + "..."


def presence_label(value: Any) -> str:
    if value is None:
        return "ausente"
    if isinstance(value, str) and not value.strip():
        return "ausente"
    if isinstance(value, list) and not value:
        return "ausente"
    return "presente"


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


def describe_analysis_sample(config: AnalysisConfig, sample: Any) -> str:
    if config.sample_strategy == "all":
        return "todos os registros elegiveis no periodo"
    sample_n = sample.get("n") if isinstance(sample, dict) else config.sample_n
    return f"ate {sample_n} contratacoes por capital"


def describe_document_sample(config: AnalysisConfig, document_sample: Any) -> str:
    counts: dict[str, Any] = {}
    if isinstance(document_sample, dict):
        raw_counts = document_sample.get("counts_by_city")
        if isinstance(raw_counts, dict):
            counts = {str(key): value for key, value in raw_counts.items()}
    if counts:
        total = sum(int(value) for value in counts.values())
        return f"ate {config.document_sample_n} por capital ({total} registros no total)"
    return f"ate {config.document_sample_n} registros por capital"
