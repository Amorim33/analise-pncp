from __future__ import annotations

import json
from typing import Any

from pncp_analysis.config import AnalysisConfig
from pncp_analysis.utils import format_percent, markdown_table


def render_report(
    config: AnalysisConfig,
    metrics: dict[str, Any],
    sampled: list[dict[str, Any]],
) -> str:
    city_metrics = metrics.get("city_metrics", [])
    field_completeness = metrics.get("field_completeness", [])
    top_sp = metrics.get("sao_paulo_top_cnpjs", [])
    sp_fragmentation = metrics.get("sao_paulo_fragmentation_evidence", {})
    sample_rows = metrics.get("sample_rows", [])
    api_examples = metrics.get("api_examples", [])
    additional_findings = metrics.get("additional_findings", [])
    document_stats = metrics.get("document_stats", [])
    limitations = metrics.get("limitations", [])

    parts = [
        "# Analise exploratoria do PNCP nas capitais do Sudeste",
        "",
        "## Resumo executivo",
        "",
        (
            "Esta analise compara contratacoes de Pregao Eletronico publicadas no PNCP "
            f"entre {config.start_date} e {config.end_date} pelas capitais do Sudeste. "
            "O desenho e exploratorio: ele busca avaliar transparencia, completude dos "
            "dados e fragmentacao institucional, sem pretender representar todos os "
            "municipios da regiao."
        ),
        "",
        "O principal achado metodologico e que Sao Paulo aparece de forma fragmentada: "
        "a consulta apenas pelo CNPJ matriz subrepresenta o municipio, enquanto a busca "
        "por codigo IBGE revela varios CNPJs municipais executivos.",
        "",
        "## Metodologia",
        "",
        markdown_table(
            ["Parametro", "Valor"],
            [
                ["Periodo", f"{config.start_date} a {config.end_date}"],
                ["Modalidade", f"{config.modality_name} ({config.modality_id})"],
                ["Amostra", f"ate {config.sample_n} contratacoes por capital"],
                ["Seed", config.seed],
            ],
        ),
        "",
        "Para Rio de Janeiro, Belo Horizonte e Vitoria, a coleta usou o CNPJ matriz do "
        "municipio. Para Sao Paulo, a coleta combinou o CNPJ matriz com uma busca por "
        "UF e codigo IBGE, filtrando orgaos municipais executivos e excluindo orgaos "
        "legislativos como a Camara Municipal.",
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
        "A amostra foi selecionada por sorteio pseudoaleatorio apos ordenacao por "
        "`numeroControlePNCP`. Quando havia mais de 10 registros, foram sorteados 10; "
        "quando havia menos, todos foram mantidos.",
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
        render_completeness_table(field_completeness),
        "",
        "## Documentos vinculados",
        "",
        render_document_stats(document_stats),
        "",
        "A presenca de objeto, datas, valores, unidade administrativa, link de origem e "
        "documentos foi usada como proxy de completude. Essa metrica nao avalia a "
        "qualidade textual dos documentos, mas indica se um cidadao ou pesquisador "
        "consegue localizar informacoes basicas para controle social.",
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
        for item in sample_rows:
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
    return markdown_table(["Capital", "Controle PNCP", "CNPJ", "Orgao", "Docs"], rows)


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


def render_limitations(limitations: Any) -> str:
    if not isinstance(limitations, list):
        return "- Nenhuma limitacao registrada."
    return "\n".join(f"- {item}" for item in limitations)


def truncate(value: str, max_length: int) -> str:
    clean = " ".join(value.split())
    if len(clean) <= max_length:
        return clean
    return clean[: max_length - 3] + "..."
