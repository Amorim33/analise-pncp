---
title: "Portal Nacional de Contratações Públicas e governo aberto: uma análise exploratória das capitais do Sudeste"
subtitle: "Transparência formal, dados abertos e fragmentação institucional"
author:
  - "PREENCHER_NOME"
date: "01/07/2026"
lang: pt-BR
course: "Governo Aberto"
instructor: "Jorge Machado"
institution: "Universidade de São Paulo"
abstract: "Este relatório analisa pregões eletrônicos publicados no PNCP entre 15/06/2025 a 15/06/2026, com foco nas prefeituras das capitais do Sudeste. O método combina coleta automatizada, análise de completude, medição de consumibilidade dos endpoints, avaliação semântica das respostas e comparação institucional entre capitais. O resultado indica boa disponibilidade de campos básicos, ressalvas em valor homologado e link de origem, além de forte fragmentação de CNPJs em São Paulo."
---

# Introdução

Este trabalho analisa o Portal Nacional de Contratações Públicas (PNCP) como infraestrutura de governo aberto nas capitais do Sudeste brasileiro. A investigação foi organizada em três questões de pesquisa:

Q1. Há completude nos dados fornecidos pelo PNCP nas prefeituras das capitais dos estados do sudeste brasileiro (São Paulo, Rio de Janeiro, Belo Horizonte e Vitória)?

Q2. Os dados das **APIs**^[**API**: interface de programação de aplicações; no contexto deste trabalho, é o meio automatizado de consulta aos dados do PNCP.] do PNCP são facilmente consumíveis?

Q3. As respostas da **API** do PNCP são semanticamente coerentes e informativas para controle social?

O PNCP é especialmente relevante porque a Lei nº 14.133/2021 o institui como ambiente nacional de divulgação de contratações públicas [@lei14133].

O argumento central é que o PNCP amplia a transparência formal ao centralizar metadados, documentos e links de origem, mas a efetividade como governo aberto depende da completude dos registros e da capacidade de reconstituir a organização administrativa de cada prefeitura. O caso de São Paulo mostra essa tensão com mais nitidez: grande parte dos registros municipais aparece fora do CNPJ matriz do município.

# Objetivos e método

O objetivo geral é avaliar, de forma exploratória, como o PNCP expressa princípios de governo aberto nas contratações das capitais do Sudeste. A pesquisa combina análise documental e computacional: coleta registros por **API**, transforma os dados em snapshots auditáveis, calcula métricas e gera relatórios reprodutíveis.

O recorte empírico considera pregões eletrônicos, modalidade 6 no PNCP, publicados entre 15/06/2025 a 15/06/2026. Foram usados os CNPJs matriz de Rio de Janeiro, Belo Horizonte e Vitória. Para São Paulo, combinou-se o CNPJ matriz com varredura por UF e código IBGE, filtrando entidades municipais executivas.

| Capital | Fonte | Registros | Páginas | Total | Limite |
| --- | --- | --- | --- | --- | --- |
| Sao Paulo | matriz | 30 | 12 | 12 |  |
| Sao Paulo | município | 17654 | 359 | 359 | todas |
| Rio de Janeiro | matriz | 896 | 23 | 23 |  |
| Belo Horizonte | matriz | 291 | 12 | 12 |  |
| Vitoria | matriz | 234 | 12 | 12 |  |

A amostra principal inclui todos os registros elegíveis no período, após deduplicação por `numeroControlePNCP`. Para a análise de documentos, foi usada subamostra determinística de até 100 registros por capital. A semente usada foi 20260608.

As métricas de Q1 medem a presença de campos essenciais, como objeto, valores, datas, unidade, link de origem e documentos. As métricas de Q2 registram duração do experimento, tempo médio de resposta e falhas observadas durante o consumo da **API**. A Q3 avalia a coerência interna e a informatividade dos registros, usando o documento principal vinculado a cada contratação da subamostra documental.

A reprodutibilidade foi organizada no repositório GitHub <https://github.com/Amorim33/analise-pncp>. O repositório versiona código Python, configurações, snapshots brutos, tabelas processadas, métricas, análise exploratória e o relatório final em Markdown, LaTeX e PDF, na branch `main`.

O processo foi assistido pelo **Codex**^[**Codex**: agente de programação e documentação usado para implementar, validar e revisar o pipeline.] em etapas de programação e documentação, sob supervisão humana. A divisão agêntica usou as **skills**^[**Skills**: instruções locais que especializam agentes para tarefas como mapear a **API**, coletar dados, revisar amostragem, avaliar qualidade semântica e redigir o relatório.] locais em `.agents/skills/`: mapeamento da **API**, coleta de dados, metodologia de amostragem, avaliação semântica e redação do relatório. As decisões substantivas, a validação das fontes e a interpretação final permanecem sob responsabilidade do autor; a declaração de uso de IA está no Apêndice B.

# Referencial teórico

Governo aberto costuma ser descrito como um arranjo que combina transparência, participação social, colaboração e prestação de contas. A Open Government Partnership associa o tema a compromissos de abertura, integridade pública e participação cidadã [@ogpDeclaration]. A OCDE também define governo aberto como uma cultura de governança que promove princípios de transparência, integridade, accountability e participação das partes interessadas [@oecd2017].

Dados abertos são uma dimensão operacional desse debate. Para que a publicação seja útil, não basta disponibilizar informação em páginas isoladas: é necessário permitir acesso, reuso, padronização e combinação com outras bases [@w3cManualDadosAbertos]. A Lei de Acesso à Informação também reforça a publicidade como regra e o sigilo como exceção [@lei12527]. Assim, transparência pública deve ser avaliada não apenas pela existência de dados, mas por sua usabilidade para fiscalização e pesquisa.

No caso brasileiro, o PNCP constitui uma infraestrutura relevante para esse tipo de análise, pois centraliza informações e documentos de contratações públicas [@pncpPortal]. A existência de API e de dados consultáveis amplia o potencial de reutilização por cidadãos, pesquisadores e jornalistas [@pncpDadosAbertos; @pncpApiConsulta].

# Desenvolvimento e análise

## Visão comparativa

| Capital | Candidatos | Amostra | CNPJs distintos | Registros na matriz | Participação da matriz |
| --- | --- | --- | --- | --- | --- |
| Sao Paulo | 2662 | 2662 | 67 | 30 | 1.1% |
| Rio de Janeiro | 896 | 896 | 1 | 896 | 100.0% |
| Belo Horizonte | 291 | 291 | 1 | 291 | 100.0% |
| Vitoria | 234 | 234 | 1 | 234 | 100.0% |

A primeira diferença relevante está na concentração institucional. Rio de Janeiro, Belo Horizonte e Vitória aparecem concentradas no CNPJ matriz no recorte adotado. São Paulo, por outro lado, apresenta múltiplos CNPJs municipais executivos associados a unidades como fundo municipal, hospital, companhia de engenharia de tráfego, secretaria e subprefeitura.

## Fragmentação em São Paulo

| Métrica | Valor |
| --- | --- |
| CNPJ matriz | 46395000000139 |
| Registros candidatos | 2662 |
| Registros no CNPJ matriz | 30 |
| Registros fora do CNPJ matriz | 2632 |
| Participação fora da matriz | 98.9% |
| CNPJs distintos | 67 |
| CNPJs fora da matriz | 66 |

Esse resultado é substantivo para governo aberto. Uma consulta limitada ao CNPJ matriz de São Paulo recuperaria apenas uma fração dos registros elegíveis. Portanto, a transparência formal do PNCP convive com uma barreira de reconstrução institucional: o cidadão precisa saber que a prefeitura pode publicar contratações por diferentes CNPJs municipais.

## Q1: completude dos dados

| Capital | Obj. | Estim. | Homol. | Data | Unid. | Link | Docs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Sao Paulo | 100.0% | 100.0% | 60.4% | 100.0% | 100.0% | 99.8% | 100.0% |
| Rio de Janeiro | 100.0% | 100.0% | 62.8% | 100.0% | 100.0% | 100.0% | 100.0% |
| Belo Horizonte | 100.0% | 100.0% | 78.0% | 100.0% | 100.0% | 96.9% | 100.0% |
| Vitoria | 100.0% | 100.0% | 66.7% | 100.0% | 100.0% | 0.0% | 100.0% |

A resposta a Q1 é positiva para os campos estruturantes do registro, mas com ressalvas relevantes. Nos registros elegíveis, objeto, valor estimado, datas básicas e unidade administrativa tiveram alta disponibilidade. A variação concentrou-se em valor homologado, link do sistema de origem e documentos, que foram avaliados na subamostra documental. Essa diferença importa para controle social porque a ausência de resultado homologado ou de link externo dificulta a reconstituição completa do processo.

Exemplos pseudoaleatórios da subamostra documental ilustram essa variação:

- Sao Paulo (`13864377000130-1-002050/2025`): data 18/11/2025; valor homologado presente; link de origem presente; 1 documento(s); objeto: REGISTRO De PREÇOS PARA O FORNECIMENTO CANULA TRAQUEOSTOMIA COM BALAO, DESCARTAVEL, ESTERIL - NR. 4,5 E SONDA ENDOTRAQUEAL, COM BALAO, RADIOPACO, D...
- Rio de Janeiro (`42498733000148-1-001315/2025`): data 24/07/2025; valor homologado presente; link de origem presente; 1 documento(s); objeto: Aquisição de Equipamento de Proteção Individual –EPI
- Belo Horizonte (`18715383000140-1-000189/2026`): data 27/03/2026; valor homologado presente; link de origem presente; 1 documento(s); objeto: O objeto da presente licitação é o registro de preços para aquisição de materiais de higiene e limpeza específicos, conforme condições e exigências...
- Vitoria (`27142058000126-1-000676/2025`): data 28/11/2025; valor homologado presente; link de origem ausente; 6 documento(s); objeto: REGISTRO DE PREÇOS VISANDO FUTURO E EVENTUAL FORNECIMENTO DE ÁGUA MINERAL GALÃO 20L

| Capital | Com documentos | Amostra | Mín. | Máx. | Média |
| --- | --- | --- | --- | --- | --- |
| Sao Paulo | 100 | 100 | 1 | 1 | 1.0 |
| Rio de Janeiro | 100 | 100 | 1 | 1 | 1.0 |
| Belo Horizonte | 100 | 100 | 1 | 2 | 1.0 |
| Vitoria | 100 | 100 | 1 | 12 | 5.3 |

## Q2: consumo da API

| Etapa | Req. | Sucesso | Média | Duração | Falhas |
| --- | --- | --- | --- | --- | --- |
| Snapshots | n/a | n/a | n/a | n/a | n/a |
| Tentativa live | 6 | 0 | n/a | 2min 56.6s | 6 |
| Documentos | 400 | 400 | 0.10s | 40.51s | 0 |
| Total |  |  |  | 3min 37.8s |  |

A resposta a Q2 é intermediária. A API é consumível por scripts, retorna JSON estruturado e expõe paginação, mas o consumo não é trivial em uma janela anual: foi necessário dividir consultas em blocos mensais, respeitar pausas entre requisições e tratar limite de taxa. A duração total do experimento inclui coleta de contratações, geração da amostra e consulta a documentos da subamostra.

Os snapshots de coleta reutilizados registravam 0 falha(s) persistente(s) na coleta bem-sucedida anterior. Na execução final, a consulta de documentos registrou 0 falha(s) persistente(s).

A tentativa live desta execução falhou e o pipeline reutilizou snapshots existentes. Erro registrado: PNCP request failed for /v1/contratacoes/publicacao: HTTP 503; content-type=text/html; body=b'<html><body><h1>503 Service Unavailable</h1> No server is available to handle this request. </body></html> '

Durante a experimentação, apareceram estes problemas: HTTP 429 em chamadas repetidas, tratado com backoff e nova tentativa.; Timeouts em paginação anual longa, mitigados pela coleta em chunks mensais de 31 dias.; Risco de resposta HTML com HTTP 200, tratado por validação de Content-Type antes do parse JSON.

## Q3: qualidade semântica e informatividade

A Q3 usa um subagent Codex como avaliador estruturado dos registros e do documento principal selecionado. Quando o texto documental não está extraído, a avaliação fica limitada ao registro da **API** e aos metadados do documento principal. O avaliador não substitui a fonte documental: snapshots, metadados, hashes de entrada e respostas brutas são preservados para auditoria. A rubrica atribui notas de 0 a 4 para coerência interna, informatividade do registro, alinhamento entre documento e **API**, e acionabilidade para controle social.

O experimento Q3 pontuou 400 de 400 registros da subamostra; 397 ficaram com texto documental insuficiente. A avaliação usou o avaliador `codex-subagent` e o prompt `q3-semantic-v1`.

| Capital | Pontuados | Texto insuf. | Amostra | Coer. | Info. | Doc/API | Acion. | Média |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Belo Horizonte | 100 | 100 | 100 | 3.96 | 3.53 | 1.00 | 1.80 | 2.57 |
| Rio de Janeiro | 100 | 98 | 100 | 3.97 | 3.71 | 1.06 | 2.00 | 2.69 |
| Sao Paulo | 100 | 99 | 100 | 3.98 | 3.36 | 1.03 | 1.91 | 2.57 |
| Vitoria | 100 | 100 | 100 | 3.95 | 2.60 | 1.00 | 0.65 | 2.05 |

Exemplos resumidos da avaliação:

- Vitoria (`27142058000126-1-000008/2026`), média 1.25: Avaliacao local Codex: status=insufficient_text; media=1.25; alinhamento lexical documento/API=0.000.
- Vitoria (`27142058000126-1-000270/2026`), média 1.25: Avaliacao local Codex: status=insufficient_text; media=1.25; alinhamento lexical documento/API=0.000.
- Vitoria (`27142058000126-1-000319/2025`), média 1.25: Avaliacao local Codex: status=insufficient_text; media=1.25; alinhamento lexical documento/API=0.000.
- Vitoria (`27142058000126-1-000634/2025`), média 1.25: Avaliacao local Codex: status=insufficient_text; media=1.25; alinhamento lexical documento/API=0.000.
- Vitoria (`27142058000126-1-000783/2025`), média 1.25: Avaliacao local Codex: status=insufficient_text; media=1.25; alinhamento lexical documento/API=0.000.

Limitações específicas da Q3:

- Avaliacao executada localmente pelo Codex como regra deterministica derivada da rubrica, sem chamada a API externa de modelo e sem conhecimento externo.
- O alinhamento documento/API usa sobreposicao lexical entre objeto, modalidade, orgao e texto extraido; baixa sobreposicao indica risco de verificabilidade, nao prova contradicao substantiva.
- Caracteres substitutos invalidos em extracoes documentais foram saneados para UTF-8 antes de hashing e gravacao; text_sha256 refere-se ao texto saneado.
- 397 documento(s) da subamostra nao tiveram texto extraido com status ok.
- 397 registro(s) receberam status insufficient_text por ausencia ou insuficiencia de texto documental.

## Constatações empíricas

- Na amostra candidata de Sao Paulo, 98.9% dos registros elegiveis ficaram fora do CNPJ matriz; nas demais capitais analisadas, os registros por CNPJ matriz concentraram 100% dos candidatos coletados.
- Sao Paulo apresentou 67 CNPJs distintos no recorte elegivel, enquanto Rio de Janeiro, Belo Horizonte e Vitoria apareceram com um CNPJ cada no recorte por matriz.
- Vitoria teve documentos vinculados em todos os itens da subamostra documental, mas nenhum dos registros elegiveis trouxe `linkSistemaOrigem`, o que reduz a rastreabilidade para o sistema de origem.
- O valor homologado apareceu com menor completude em Sao Paulo (60.4%), indicando que parte dos registros estava em fase anterior ao resultado ou sem homologacao registrada no recorte.
- A quantidade de documentos anexados variou de forma relevante: em Vitoria, um item da amostra chegou a 12 documentos, enquanto outros municipios tiveram padrao mais concentrado.

# Conclusões

A análise indica que o PNCP é uma infraestrutura importante de governo aberto: ele centraliza registros, expõe campos padronizados, oferece documentos e permite automação por API. Esses elementos fortalecem a transparência formal e criam condições para controle social.

Ao mesmo tempo, a comparação mostra que abertura não é sinônimo automático de inteligibilidade. A fragmentação de CNPJs em São Paulo torna a busca mais complexa e pode subestimar a atividade contratual municipal quando o pesquisador consulta apenas o CNPJ matriz. A contribuição do trabalho está em mostrar que a avaliação de governo aberto deve observar também a arquitetura institucional dos dados.

Como conclusão regional exploratória, as capitais do Sudeste analisadas apresentam boa disponibilidade básica de dados e documentos no PNCP, mas diferem na forma de organização dos registros. A agenda de melhoria passa por documentação mais clara dos CNPJs/unidades, maior completude de links de origem, respostas semanticamente coerentes e mecanismos que facilitem ao cidadão reconstruir o universo de órgãos vinculados a cada prefeitura.

# Referências

::: {#refs}
:::

\appendix

# Apêndice A: exemplos compactos da API

## Sao Paulo - exemplo fora do CNPJ matriz

- Controle PNCP: `01164292000160-1-000020/2026`
- CNPJ/órgão: `01164292000160` — MUNICIPIO DE CACU
- Unidade: PREFEITURA MUNICIPAL DE CAÇU
- Valor estimado: 137600.4
- Valor homologado: não informado
- Situação: Divulgada no PNCP
- Documentos listados no exemplo: 0
- Objeto: CONTRATAÇÃO DE EMPRESA DO RAMO PARA A AQUISIÇÃO E INSTALAÇÃO DE PARQUE INFANTIL, DEVIDAMENTE CERTIFICADO POR ÓRGÃO COMPETENTE, PARA ATENDER AS NECESSIDADES DO FUNDO MUNICIPAL DE EDUCAÇÃO/FME, CONFORME EMENDA PARLAMENTAR Nº 1299.2/2025, PROCESSO Nº 202500005...

## Sao Paulo - exemplo no CNPJ matriz

- Controle PNCP: `46395000000139-1-000007/2026`
- CNPJ/órgão: `46395000000139` — MUNICIPIO DE SAO PAULO
- Unidade: PMSP - SECRETARIA DO GOVERNO MUNICIPAL
- Valor estimado: 62640.7
- Valor homologado: 42066.57
- Situação: Divulgada no PNCP
- Documentos listados no exemplo: 0
- Objeto: Aquisição de materiais de construção, abrangendo itens das linhas hidráulica, elétrica, ferragens, pintura, alvenaria, acabamentos e correlatos, conforme as especificações, quantidades e condições estabelecidas neste Termo de Referência considerando AUSÊNCI...

## Rio de Janeiro

- Controle PNCP: `42498733000148-1-000104/2026`
- CNPJ/órgão: `42498733000148` — MUNICIPIO DE RIO DE JANEIRO
- Unidade: PREFEITURA MUNICIPAL DO RIO DE JANEIRO - RJ
- Valor estimado: 0.0
- Valor homologado: não informado
- Situação: Divulgada no PNCP
- Documentos listados no exemplo: 0
- Objeto: CoNTRATAÇÃO DE EMPRESA ESPECIALIZADA PARA PRESTAÇÃO DE SERVIÇOS DE PLANEJAMENTO, ORGANIZAÇÃO, EXECUÇÃO, ACOMPANHAMENTO, FORNECIMENTO DE BENS E INSUMOS, INFRAESTRUTURA E APOIO LOGÍSTICO, VISANDO A REALIZAÇÃO DO BAILE DA CINELÂNDIA E DESFILES DA AVENIDA CHILE...

## Belo Horizonte

- Controle PNCP: `18715383000140-1-000024/2026`
- CNPJ/órgão: `18715383000140` — MUNICIPIO DE BELO HORIZONTE
- Unidade: PREF.MUN.DE BELO HORIZONTE
- Valor estimado: 3585413.35
- Valor homologado: 1969468.81
- Situação: Divulgada no PNCP
- Documentos listados no exemplo: 0
- Objeto: O objeto da presente licitação é a aquisição de COLETES DE PROTEÇÃO BALÍSTICA FLEXÍVEL, PARA USO POLICIAL, NÍVEL DE PROTEÇÃO III-A, COM CAPA EXTERNA TIPO MODULAR (COM CAPA SOBRESSALENTE TIPO MODULAR), com a finalidade de atender atividades operacionais da G...


# Apêndice B: declaração de uso de IA

Este trabalho utilizou ferramentas de inteligência artificial generativa para apoio à programação do pipeline de coleta e análise, organização dos resultados, revisão textual e geração inicial do relatório. A seleção do tema, a validação das fontes, a interpretação dos resultados e a versão final são de responsabilidade do(s) autor(es).

# Apêndice C: limitações metodológicas

A pesquisa é exploratória e não representa todos os municípios do Sudeste. A API de consulta por publicação limita cada requisição a janelas de até 365 dias; por isso, o recorte usa a maior janela aceita em uma consulta reprodutível. Além disso, documentos vinculados foram analisados por subamostra determinística. A avaliação semântica depende da extração de texto ou dos metadados do documento principal e de uma rodada preservada do subagent Codex avaliador; seus resultados devem ser lidos como apoio estruturado à análise, não como fonte primária. Os resultados podem mudar com novas publicações, retificações ou alterações na API do PNCP.
