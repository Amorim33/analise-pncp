from __future__ import annotations

import json
from typing import Any

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
    semantic_quality = metrics.get("semantic_quality", {})
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
        (
            "- Q3. As respostas da **API** do PNCP sao semanticamente coerentes e "
            "informativas para controle social?"
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
                ["Amostra Q3", "documento principal da subamostra documental"],
                ["Modelo Q3", config.semantic.model],
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
            "metodologia de amostragem, avaliacao semantica e redacao do relatorio. "
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
            "Para Q2, o pipeline registrou a duracao da coleta e das chamadas ao "
            "endpoint de documentos, alem do tempo medio de resposta bem-sucedida. "
            "A facilidade de consumo e parcial: a API e estruturada e paginada, mas "
            "exige controle de janela temporal, backoff para limite de taxa e validacao "
            "de `Content-Type` para evitar parse de respostas nao JSON."
        ),
        "",
        render_api_performance(collection_metadata, api_experiment, pipeline_metadata),
        "",
        render_api_error_notes(collection_metadata, api_experiment, pipeline_metadata),
        "",
        "## Qualidade semantica e informatividade",
        "",
        (
            "Para Q3, o pipeline seleciona um documento principal por contratacao da "
            "subamostra documental e usa um subagent Codex como avaliador estruturado. "
            "Quando o texto documental nao esta extraido, a avaliacao fica limitada ao "
            "registro da **API** e aos metadados do documento principal. O avaliador nao "
            "e fonte de verdade: a evidencia auditavel fica nos snapshots, metadados, "
            "hashes dos inputs e respostas preservadas."
        ),
        "",
        render_semantic_quality(semantic_quality),
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
            "completude documental, da padronizacao dos registros, da qualidade "
            "semantica das informacoes retornadas e da facilidade de reconstituir o "
            "universo institucional de cada prefeitura."
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
    document_duration = optional_float(api_experiment.get("duration_seconds")) if isinstance(
        api_experiment,
        dict,
    ) else None
    pipeline_duration = optional_float(pipeline_metadata.get("duration_seconds"))
    if pipeline_duration is None:
        pipeline_duration = sum(
            value for value in [collection_duration, document_duration] if value
        )

    attempt = pipeline_metadata.get("collection_attempt", {})
    attempt_failed = isinstance(attempt, dict) and attempt.get("status") == "failed"
    rows = [
        performance_row(
            "Snapshots de contratações" if attempt_failed else "Coleta de contratações",
            collection_perf,
            collection_duration,
        ),
    ]
    if attempt_failed:
        attempt_perf = attempt.get("api_performance", {})
        rows.append(
            performance_row(
                "Tentativa live de coleta",
                attempt_perf if isinstance(attempt_perf, dict) else {},
                optional_float(attempt.get("duration_seconds")),
            )
        )
    rows.extend(
        [
            performance_row("Consulta de documentos", document_perf, document_duration),
            [
                "Experimento total do relatório",
                "",
                "",
                "",
                format_seconds(pipeline_duration),
                "",
            ],
        ]
    )
    return markdown_table(
        ["Etapa", "Requisições", "Sucessos", "Tempo médio", "Duração", "Falhas"],
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
    collection_failure_count = (
        len(collection_failures) if isinstance(collection_failures, list) else 0
    )
    if attempt_failed:
        lines = [
            (
                "- Os snapshots de coleta reutilizados registravam "
                f"{collection_failure_count} falhas persistentes na coleta bem-sucedida "
                "anterior."
            ),
            (
                "- Na execução final, a consulta de documentos registrou "
                f"{len(document_failures)} falhas persistentes."
            ),
        ]
    else:
        lines = [
            (
                "- Na execução final, a coleta registrou "
                f"{collection_failure_count} falhas persistentes."
            ),
            (
                "- Na execução final, a consulta de documentos registrou "
                f"{len(document_failures)} falhas persistentes."
            ),
        ]
    if attempt_failed:
        lines.append(
            "- A tentativa live desta execução falhou e o pipeline reutilizou snapshots "
            f"existentes. Erro registrado: {truncate(str(attempt.get('error') or ''), 220)}"
        )
    lines.extend(f"- Durante a experimentação: {item}" for item in observed_errors)
    return "\n".join(lines)


def render_semantic_quality(semantic_quality: Any) -> str:
    if not isinstance(semantic_quality, dict) or not semantic_quality:
        return (
            "_A etapa Q3 ainda nao foi executada. Rode "
            "`uv run pncp-analysis semantic` para gerar os artefatos semanticos._"
        )

    by_city = semantic_quality.get("by_city", [])
    rows = []
    if isinstance(by_city, list):
        for item in by_city:
            if isinstance(item, dict):
                rows.append(
                    [
                        item.get("city", ""),
                        item.get("scored_count", item.get("evaluated_count", 0)),
                        item.get("insufficient_text_count", 0),
                        item.get("sample_count", 0),
                        format_score(item.get("avg_coerencia_interna")),
                        format_score(item.get("avg_informatividade_do_registro")),
                        format_score(item.get("avg_alinhamento_documento_api")),
                        format_score(item.get("avg_acionabilidade_controle_social")),
                        format_score(item.get("avg_score_medio")),
                    ]
                )

    table = markdown_table(
        [
            "Capital",
            "Pontuados",
            "Texto insuf.",
            "Amostra",
            "Coer.",
            "Info.",
            "Doc/API",
            "Acion.",
            "Media",
        ],
        rows,
    )
    overall = semantic_quality.get("overall", {})
    if not isinstance(overall, dict):
        overall = {}
    scored_count = semantic_quality.get(
        "scored_count",
        overall.get("scored_count", semantic_quality.get("evaluated_count", 0)),
    )
    lines = [
        (
            f"A Q3 usou o prompt `{semantic_quality.get('prompt_version', '')}` e o "
            f"schema `{semantic_quality.get('schema_version', '')}`. "
            f"O avaliador registrado foi `{semantic_quality.get('model', '')}`. "
            f"Foram pontuados {scored_count} "
            f"de {semantic_quality.get('sample_count', 0)} registros da subamostra; "
            f"{semantic_quality.get('insufficient_text_count', 0)} ficaram com texto "
            "documental insuficiente."
        ),
        "",
        table,
    ]

    examples = semantic_quality.get("examples", [])
    if isinstance(examples, list) and examples:
        lines.extend(["", "Exemplos de avaliacao:", ""])
        for item in examples[:6]:
            if isinstance(item, dict):
                alerts = item.get("alertas", [])
                alert_text = (
                    "; ".join(str(alert) for alert in alerts)
                    if isinstance(alerts, list)
                    else ""
                )
                lines.append(
                    "- "
                    f"{item.get('city', '')} (`{item.get('numeroControlePNCP', '')}`), "
                    f"media {format_score(item.get('score_medio'))}: "
                    f"{truncate(str(item.get('resumo') or ''), 160)}"
                    + (f" Alertas: {truncate(alert_text, 160)}" if alert_text else "")
                )

    limitations = semantic_quality.get("limitations", [])
    if isinstance(limitations, list) and limitations:
        lines.extend(["", "Limitacoes especificas da Q3:", ""])
        lines.extend(f"- {item}" for item in limitations)
    return "\n".join(lines)


def format_score(value: Any) -> str:
    numeric = optional_float(value)
    return "n/a" if numeric is None else f"{numeric:.2f}"


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


def optional_float(value: Any) -> float | None:
    if isinstance(value, int | float):
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
