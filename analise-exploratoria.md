# Analise exploratoria do PNCP nas capitais do Sudeste

## Resumo executivo

Esta analise compara contratacoes de Pregao Eletronico publicadas no PNCP entre 2026-01-01 e 2026-05-31 pelas capitais do Sudeste. O desenho e exploratorio: ele busca avaliar transparencia, completude dos dados e fragmentacao institucional, sem pretender representar todos os municipios da regiao.

O principal achado metodologico e que Sao Paulo aparece de forma fragmentada: a consulta apenas pelo CNPJ matriz subrepresenta o municipio, enquanto a busca por codigo IBGE revela varios CNPJs municipais executivos.

## Metodologia

| Parametro | Valor |
| --- | --- |
| Periodo | 2026-01-01 a 2026-05-31 |
| Modalidade | Pregao - Eletronico (6) |
| Amostra | ate 10 contratacoes por capital |
| Seed | 20260608 |

Para Rio de Janeiro, Belo Horizonte e Vitoria, a coleta usou o CNPJ matriz do municipio. Para Sao Paulo, a coleta combinou o CNPJ matriz com uma busca por UF e codigo IBGE, filtrando orgaos municipais executivos e excluindo orgaos legislativos como a Camara Municipal.

## Amostra

| Capital | Registros candidatos | Amostra | CNPJs distintos | Registros no CNPJ matriz | Participacao da matriz |
| --- | --- | --- | --- | --- | --- |
| Sao Paulo | 61 | 10 | 10 | 6 | 9.8% |
| Rio de Janeiro | 347 | 10 | 1 | 347 | 100.0% |
| Belo Horizonte | 90 | 10 | 1 | 90 | 100.0% |
| Vitoria | 98 | 10 | 1 | 98 | 100.0% |

A amostra foi selecionada por sorteio pseudoaleatorio apos ordenacao por `numeroControlePNCP`. Quando havia mais de 10 registros, foram sorteados 10; quando havia menos, todos foram mantidos.

## Resultados

| Capital | Controle PNCP | CNPJ | Orgao | Docs |
| --- | --- | --- | --- | --- |
| Sao Paulo | 13864377000130-1-000007/2026 | 13864377000130 | FUNDO MUNICIPAL DE SAUDE - FMS | 1 |
| Sao Paulo | 13864377000130-1-000013/2026 | 13864377000130 | FUNDO MUNICIPAL DE SAUDE - FMS | 1 |
| Sao Paulo | 13864377000130-1-000014/2026 | 13864377000130 | FUNDO MUNICIPAL DE SAUDE - FMS | 1 |
| Sao Paulo | 13864377000130-1-000026/2026 | 13864377000130 | FUNDO MUNICIPAL DE SAUDE - FMS | 1 |
| Sao Paulo | 13864377000130-1-000031/2026 | 13864377000130 | FUNDO MUNICIPAL DE SAUDE - FMS | 1 |
| Sao Paulo | 13864377000130-1-000034/2026 | 13864377000130 | FUNDO MUNICIPAL DE SAUDE - FMS | 1 |
| Sao Paulo | 13864377000130-1-002230/2025 | 13864377000130 | FUNDO MUNICIPAL DE SAUDE - FMS | 1 |
| Sao Paulo | 13864377000130-1-002232/2025 | 13864377000130 | FUNDO MUNICIPAL DE SAUDE - FMS | 1 |
| Sao Paulo | 46395000000139-1-000028/2026 | 46395000000139 | MUNICIPIO DE SAO PAULO | 1 |
| Sao Paulo | 74118514000182-1-000001/2026 | 74118514000182 | SAO PAULO SECRETARIA DO VERDE E DO MEIO AMBIENTE | 1 |
| Rio de Janeiro | 42498733000148-1-000127/2026 | 42498733000148 | MUNICIPIO DE RIO DE JANEIRO | 1 |
| Rio de Janeiro | 42498733000148-1-000324/2026 | 42498733000148 | MUNICIPIO DE RIO DE JANEIRO | 1 |
| Rio de Janeiro | 42498733000148-1-000345/2026 | 42498733000148 | MUNICIPIO DE RIO DE JANEIRO | 1 |
| Rio de Janeiro | 42498733000148-1-000498/2026 | 42498733000148 | MUNICIPIO DE RIO DE JANEIRO | 1 |
| Rio de Janeiro | 42498733000148-1-000519/2026 | 42498733000148 | MUNICIPIO DE RIO DE JANEIRO | 1 |
| Rio de Janeiro | 42498733000148-1-000525/2026 | 42498733000148 | MUNICIPIO DE RIO DE JANEIRO | 1 |
| Rio de Janeiro | 42498733000148-1-000811/2026 | 42498733000148 | MUNICIPIO DE RIO DE JANEIRO | 1 |
| Rio de Janeiro | 42498733000148-1-000822/2026 | 42498733000148 | MUNICIPIO DE RIO DE JANEIRO | 1 |
| Rio de Janeiro | 42498733000148-1-000868/2026 | 42498733000148 | MUNICIPIO DE RIO DE JANEIRO | 1 |
| Rio de Janeiro | 42498733000148-1-001034/2026 | 42498733000148 | MUNICIPIO DE RIO DE JANEIRO | 1 |
| Belo Horizonte | 18715383000140-1-000178/2026 | 18715383000140 | MUNICIPIO DE BELO HORIZONTE | 1 |
| Belo Horizonte | 18715383000140-1-000272/2026 | 18715383000140 | MUNICIPIO DE BELO HORIZONTE | 1 |
| Belo Horizonte | 18715383000140-1-000344/2026 | 18715383000140 | MUNICIPIO DE BELO HORIZONTE | 1 |
| Belo Horizonte | 18715383000140-1-001094/2025 | 18715383000140 | MUNICIPIO DE BELO HORIZONTE | 1 |
| Belo Horizonte | 18715383000140-1-001105/2025 | 18715383000140 | MUNICIPIO DE BELO HORIZONTE | 1 |
| Belo Horizonte | 18715383000140-1-001189/2025 | 18715383000140 | MUNICIPIO DE BELO HORIZONTE | 1 |
| Belo Horizonte | 18715383000140-1-001216/2025 | 18715383000140 | MUNICIPIO DE BELO HORIZONTE | 1 |
| Belo Horizonte | 18715383000140-1-001223/2025 | 18715383000140 | MUNICIPIO DE BELO HORIZONTE | 1 |
| Belo Horizonte | 18715383000140-1-001225/2025 | 18715383000140 | MUNICIPIO DE BELO HORIZONTE | 1 |
| Belo Horizonte | 18715383000140-1-001232/2025 | 18715383000140 | MUNICIPIO DE BELO HORIZONTE | 1 |
| Vitoria | 27142058000126-1-000034/2026 | 27142058000126 | MUNICIPIO DE VITORIA | 2 |
| Vitoria | 27142058000126-1-000080/2026 | 27142058000126 | MUNICIPIO DE VITORIA | 4 |
| Vitoria | 27142058000126-1-000090/2026 | 27142058000126 | MUNICIPIO DE VITORIA | 4 |
| Vitoria | 27142058000126-1-000176/2026 | 27142058000126 | MUNICIPIO DE VITORIA | 3 |
| Vitoria | 27142058000126-1-000202/2026 | 27142058000126 | MUNICIPIO DE VITORIA | 12 |
| Vitoria | 27142058000126-1-000216/2026 | 27142058000126 | MUNICIPIO DE VITORIA | 2 |
| Vitoria | 27142058000126-1-000233/2026 | 27142058000126 | MUNICIPIO DE VITORIA | 3 |
| Vitoria | 27142058000126-1-000267/2026 | 27142058000126 | MUNICIPIO DE VITORIA | 4 |
| Vitoria | 27142058000126-1-000268/2026 | 27142058000126 | MUNICIPIO DE VITORIA | 2 |
| Vitoria | 27142058000126-1-000797/2025 | 27142058000126 | MUNICIPIO DE VITORIA | 20 |

## Fragmentacao de CNPJs em Sao Paulo

A tabela abaixo mostra os principais CNPJs municipais encontrados no recorte de Sao Paulo apos o filtro de orgaos executivos municipais.

| CNPJ | Razao social | Registros |
| --- | --- | --- |
| 13864377000130 | FUNDO MUNICIPAL DE SAUDE - FMS | 38 |
| 46395000000139 | MUNICIPIO DE SAO PAULO | 6 |
| 47902648000117 | PMSP - COMPANHIA DE ENGENHARIA DE TRÁFEGO | 6 |
| 46854998000192 | HOSPITAL DO SERVIDOR PUBLICO MUNICIPAL | 3 |
| 49269251000165 | SECRETARIA MUNICIPAL DE GESTAO - SG | 2 |
| 74118514000182 | SAO PAULO SECRETARIA DO VERDE E DO MEIO AMBIENTE | 2 |
| 05245375000135 | SECRETARIA MUNICIPAL DE SEGURANCA URBANA - SMSU | 1 |
| 05969123000159 | SUBPREFEITURA VILA PRUDENTE | 1 |
| 46392114000125 | SECRETARIA MUNICIPAL DE EDUCACAO | 1 |
| 46392130000118 | SECRETARIA MUNICIPAL DA FAZENDA | 1 |

Esse resultado sugere que a transparencia via PNCP nao depende apenas da existencia do portal, mas tambem da forma como a administracao estrutura e publica seus registros. Uma busca pelo CNPJ matriz de Sao Paulo tende a perder contratacoes relevantes de secretarias, fundos, empresas e unidades municipais.

## Completude dos dados

| Capital | Campo | Presentes | Amostra | Percentual |
| --- | --- | --- | --- | --- |
| Sao Paulo | Objeto | 10 | 10 | 100.0% |
| Sao Paulo | Valor estimado | 10 | 10 | 100.0% |
| Sao Paulo | Valor homologado | 7 | 10 | 70.0% |
| Sao Paulo | Data de publicacao | 10 | 10 | 100.0% |
| Sao Paulo | Abertura de proposta | 10 | 10 | 100.0% |
| Sao Paulo | Encerramento de proposta | 10 | 10 | 100.0% |
| Sao Paulo | Unidade | 10 | 10 | 100.0% |
| Sao Paulo | Link de origem | 10 | 10 | 100.0% |
| Sao Paulo | Documentos | 10 | 10 | 100.0% |
| Rio de Janeiro | Objeto | 10 | 10 | 100.0% |
| Rio de Janeiro | Valor estimado | 10 | 10 | 100.0% |
| Rio de Janeiro | Valor homologado | 5 | 10 | 50.0% |
| Rio de Janeiro | Data de publicacao | 10 | 10 | 100.0% |
| Rio de Janeiro | Abertura de proposta | 10 | 10 | 100.0% |
| Rio de Janeiro | Encerramento de proposta | 10 | 10 | 100.0% |
| Rio de Janeiro | Unidade | 10 | 10 | 100.0% |
| Rio de Janeiro | Link de origem | 10 | 10 | 100.0% |
| Rio de Janeiro | Documentos | 10 | 10 | 100.0% |
| Belo Horizonte | Objeto | 10 | 10 | 100.0% |
| Belo Horizonte | Valor estimado | 10 | 10 | 100.0% |
| Belo Horizonte | Valor homologado | 7 | 10 | 70.0% |
| Belo Horizonte | Data de publicacao | 10 | 10 | 100.0% |
| Belo Horizonte | Abertura de proposta | 10 | 10 | 100.0% |
| Belo Horizonte | Encerramento de proposta | 10 | 10 | 100.0% |
| Belo Horizonte | Unidade | 10 | 10 | 100.0% |
| Belo Horizonte | Link de origem | 9 | 10 | 90.0% |
| Belo Horizonte | Documentos | 10 | 10 | 100.0% |
| Vitoria | Objeto | 10 | 10 | 100.0% |
| Vitoria | Valor estimado | 10 | 10 | 100.0% |
| Vitoria | Valor homologado | 4 | 10 | 40.0% |
| Vitoria | Data de publicacao | 10 | 10 | 100.0% |
| Vitoria | Abertura de proposta | 10 | 10 | 100.0% |
| Vitoria | Encerramento de proposta | 10 | 10 | 100.0% |
| Vitoria | Unidade | 10 | 10 | 100.0% |
| Vitoria | Link de origem | 0 | 10 | 0.0% |
| Vitoria | Documentos | 10 | 10 | 100.0% |

A presenca de objeto, datas, valores, unidade administrativa, link de origem e documentos foi usada como proxy de completude. Essa metrica nao avalia a qualidade textual dos documentos, mas indica se um cidadao ou pesquisador consegue localizar informacoes basicas para controle social.

## Limitacoes

- A comparacao e exploratoria e nao representa todos os municipios do Sudeste.
- Sao Paulo possui registros municipais distribuidos em varios CNPJs, o que exige filtro por municipio e orgao.
- A varredura municipal de Sao Paulo usa limite operacional de 5 paginas da API.
- A API pode retornar payload HTML de bloqueio com HTTP 200; o coletor valida Content-Type e registra falhas.

## Conclusao regional

O PNCP oferece uma infraestrutura relevante de governo aberto para as capitais do Sudeste, pois centraliza registros, padroniza campos e permite consulta por API. No entanto, a comparacao mostra que a abertura formal dos dados nao elimina assimetrias de acesso. A fragmentacao de CNPJs em Sao Paulo e um achado substantivo: mesmo com dados publicos, a capacidade de controle social depende de conhecer a organizacao administrativa por tras dos registros.

Assim, a conclusao regional e que o PNCP fortalece a transparencia formal, mas sua efetividade como instrumento de governo aberto depende da completude documental, da padronizacao dos registros e da facilidade de reconstituir o universo institucional de cada prefeitura.

## Reproducibilidade

```bash
uv sync --extra dev
uv run pncp-analysis run-all
make check
```

## Referencias tecnicas

- API de consulta PNCP: <https://pncp.gov.br/pncp-consulta/v3/api-docs>
- API PNCP: <https://pncp.gov.br/pncp-api/v3/api-docs>
- Modalidades PNCP: <https://pncp.gov.br/api/pncp/v1/modalidades>
