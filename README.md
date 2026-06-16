# Analise PNCP

Repositorio de analise exploratoria das contratacoes publicas publicadas no
Portal Nacional de Contratacoes Publicas (PNCP) pelas capitais do Sudeste.

O recorte inicial usa:

- periodo: `15/06/2025` a `15/06/2026`;
- modalidade: Pregao Eletronico, codigo `6`;
- capitais: Sao Paulo, Rio de Janeiro, Belo Horizonte e Vitoria;
- amostra principal: todos os registros elegiveis no periodo;
- amostra documental: ate 100 contratacoes por capital, com sorteio deterministico.

Os artefatos principais sao `analise-exploratoria.md` e
`report/output/relatorio-final.pdf`.

## Objetivo

Comparar, de forma exploratoria, como as capitais do Sudeste aparecem no PNCP em
termos de transparencia, completude de dados e fragmentacao institucional. O
caso de Sao Paulo recebe uma etapa propria porque os registros aparecem
distribuidos em varios CNPJs municipais, e nao apenas no CNPJ matriz do
municipio.

## Fontes

- API de consulta: <https://pncp.gov.br/pncp-consulta/v3/api-docs>
- API PNCP: <https://pncp.gov.br/pncp-api/v3/api-docs>
- Modalidades: <https://pncp.gov.br/api/pncp/v1/modalidades>

## Setup

```bash
uv sync --extra dev
```

## Execucao

Rodar o fluxo completo:

```bash
uv run pncp-analysis run-all
uv run pncp-analysis paper
```

Ou executar por etapas:

```bash
uv run pncp-analysis collect
uv run pncp-analysis sample
uv run pncp-analysis analyze
uv run pncp-analysis report
uv run pncp-analysis paper --tex-only
```

Saidas:

- `data/raw/`: snapshots JSON da API;
- `data/processed/`: registros elegiveis, subamostra documental, metricas e
  tabelas derivadas;
- `analise-exploratoria.md`: relatorio final.
- `report/relatorio-final.md`: fonte academica com citacoes Pandoc.
- `report/output/relatorio-final.tex`: fonte LaTeX.
- `report/output/relatorio-final.pdf`: PDF final.

O relatorio inclui exemplos compactos de registros retornados pela API, metricas
de completude, estatisticas de documentos vinculados e evidencias especificas
para sustentar a fragmentacao de CNPJs em Sao Paulo.

## Relatorio final em LaTeX/PDF

Edite `config/paper.yaml` para preencher autoria, instituicao e declaracao de
uso de IA. Em modo `draft`, placeholders sao permitidos. Em modo `final`, o
comando falha se ainda houver metadados iniciados por `PREENCHER`, exceto quando
`--allow-placeholders` for usado explicitamente.

Gerar o paper:

```bash
uv run pncp-analysis paper
```

Gerar apenas LaTeX:

```bash
uv run pncp-analysis paper --tex-only
```

Rodar tudo:

```bash
make final
```

## Metodologia operacional

1. Coletar contratacoes por data de publicacao e modalidade `6`.
2. Para Rio de Janeiro, Belo Horizonte e Vitoria, usar o CNPJ matriz de cada
   municipio.
3. Para Sao Paulo, coletar tanto o CNPJ matriz quanto a consulta por municipio
   IBGE `3550308`, filtrando orgaos municipais executivos. Com
   `api.municipality_scan_max_pages: null`, a varredura municipal coleta todas
   as paginas retornadas pela API na janela anual.
4. Ordenar os registros por `numeroControlePNCP`, deduplicar e manter todos os
   registros elegiveis como amostra principal.
5. Criar uma subamostra documental deterministica de ate 100 registros por
   capital e consultar os documentos vinculados no endpoint de arquivos.
6. Gerar metricas de volume, fragmentacao de CNPJ, completude de campos e
   presenca de documentos.

## Validacao

```bash
make check
```

O comando roda:

- `ruff check .`
- `mypy src`
- `pytest`

## Observacoes sobre a API

Algumas combinacoes de parametros podem retornar uma pagina HTML "Request
Rejected" com status HTTP 200. O coletor valida `Content-Type`, tenta bases
alternativas da API e registra falhas de coleta em `data/raw/collection_metadata.json`.

## Estrutura de agentes

As skills locais em `.agents/skills/` dividem o trabalho entre mapeamento da API,
coleta, metodologia de amostragem e redacao do relatorio. Elas servem como
instrucoes para agentes que venham a manter ou repetir a analise.
