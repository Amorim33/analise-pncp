from __future__ import annotations

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
    sample_rows = metrics.get("sample_rows", [])
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
        "## Fragmentacao de CNPJs em Sao Paulo",
        "",
        "A tabela abaixo mostra os principais CNPJs municipais encontrados no recorte de "
        "Sao Paulo apos o filtro de orgaos executivos municipais.",
        "",
        render_sp_top_table(top_sp),
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


def render_limitations(limitations: Any) -> str:
    if not isinstance(limitations, list):
        return "- Nenhuma limitacao registrada."
    return "\n".join(f"- {item}" for item in limitations)
