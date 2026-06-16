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
abstract: "Este relatório analisa pregões eletrônicos publicados no PNCP entre 15/06/2025 a 15/06/2026, com foco nas prefeituras das capitais do Sudeste. O método combina coleta automatizada dos dados, verificação de quão completos eles são, medição da facilidade de obtê-los pela API e comparação entre as capitais. O resultado indica boa disponibilidade dos campos básicos, com ressalvas no valor homologado e no link para o sistema de origem, além de forte fragmentação de CNPJs em São Paulo."
---

# Introdução

Este trabalho analisa o Portal Nacional de Contratações Públicas (PNCP) como infraestrutura de governo aberto nas capitais do Sudeste brasileiro. A investigação foi organizada em duas questões de pesquisa:

Q1. Há completude nos dados fornecidos pelo PNCP nas prefeituras das capitais dos estados do sudeste brasileiro (São Paulo, Rio de Janeiro, Belo Horizonte e Vitória)? Ou seja, os campos essenciais de cada contratação (objeto, valores, datas, documentos) chegam preenchidos?

Q2. Os dados das **APIs**^[**API**: sigla em inglês para interface de programação de aplicações; é o canal automatizado pelo qual um programa consulta os dados do PNCP, sem depender de cliques manuais no site.] do PNCP são facilmente consumíveis? Em outras palavras, um cidadão, pesquisador ou jornalista consegue baixar os dados de forma automática, rápida e confiável?

O PNCP é especialmente relevante porque a Lei nº 14.133/2021 o institui como ambiente nacional de divulgação de contratações públicas [@lei14133].

O argumento central é que o PNCP amplia a transparência formal ao centralizar metadados, documentos e links de origem, mas a efetividade como governo aberto depende da completude dos registros e da capacidade de reconstituir a organização administrativa de cada prefeitura. O caso de São Paulo mostra essa tensão com mais nitidez: grande parte dos registros municipais aparece fora do CNPJ matriz do município.

# Objetivos e método

O objetivo geral é avaliar, de forma exploratória, como o PNCP expressa princípios de governo aberto nas contratações das capitais do Sudeste. A pesquisa combina análise documental e computacional: coleta registros por **API**, guarda cada resposta em cópias datadas e auditáveis^[Cópia datada (ou *snapshot*): arquivo que preserva exatamente o que a fonte respondeu em determinado momento, permitindo conferência posterior.], calcula indicadores e gera relatórios que podem ser refeitos do zero por qualquer pessoa.

O recorte empírico considera pregões eletrônicos^[Pregão eletrônico: forma de licitação feita pela internet, em que fornecedores disputam o fornecimento de bens e serviços; no PNCP corresponde à modalidade de código 6.] publicados entre 15/06/2025 a 15/06/2026. Foram usados os CNPJs^[CNPJ: Cadastro Nacional da Pessoa Jurídica, número único que identifica cada órgão ou empresa. O CNPJ matriz é o número principal da prefeitura; secretarias, fundos e autarquias podem ter CNPJs próprios.] matriz de Rio de Janeiro, Belo Horizonte e Vitória. Para São Paulo, combinou-se o CNPJ matriz com uma varredura por estado (UF) e por código do município no IBGE, mantendo apenas órgãos municipais do poder executivo.

| Capital | Fonte | Registros | Páginas | Total | Limite |
| --- | --- | --- | --- | --- | --- |
| Sao Paulo | matriz | 30 | 12 | 12 |  |
| Sao Paulo | município | 17654 | 359 | 359 | todas |
| Rio de Janeiro | matriz | 896 | 23 | 23 |  |
| Belo Horizonte | matriz | 291 | 12 | 12 |  |
| Vitoria | matriz | 233 | 12 | 12 |  |

A amostra principal inclui todos os registros elegíveis no período, depois de removidas as duplicatas pelo número de controle do PNCP (campo `numeroControlePNCP`). Para a análise de documentos, foi usada uma subamostra de até 100 registros por capital, sorteada de forma reproduzível^[Subamostra reproduzível: a seleção usa um valor de partida fixo (a *semente*), de modo que qualquer pessoa que repita o processo obtém exatamente os mesmos registros.]. A semente usada foi 20260608.

As métricas de Q1 medem a presença dos campos essenciais de cada contratação: objeto, valores, datas, unidade administrativa, link para o sistema de origem e documentos. As métricas de Q2 medem a facilidade de obter esses dados de forma automática: quanto tempo cada consulta levou, como esse tempo se distribuiu e quantas consultas falharam durante o acesso à **API**.

A reprodutibilidade foi organizada no repositório GitHub <https://github.com/Amorim33/analise-pncp>. O repositório versiona código Python, configurações, cópias brutas das respostas, tabelas processadas, métricas, análise exploratória e o relatório final em Markdown, LaTeX e PDF, na branch `main`.

O processo foi assistido pelo **Codex**^[**Codex**: agente de inteligência artificial para programação e documentação, usado para implementar, validar e revisar o conjunto de programas da análise.] em etapas de programação e documentação, sob supervisão humana. A divisão de tarefas entre agentes usou as **skills**^[**Skills**: instruções locais que especializam cada agente para uma tarefa, como mapear a **API**, coletar dados, revisar a amostragem e redigir o relatório.] locais em [`.agents/skills/`](https://github.com/Amorim33/analise-pncp/tree/main/.agents/skills): mapeamento da **API**, coleta de dados, metodologia de amostragem e redação do relatório. As decisões substantivas, a validação das fontes e a interpretação final permanecem sob responsabilidade do autor; a declaração de uso de IA está no Apêndice B.

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
| Vitoria | 233 | 233 | 1 | 233 | 100.0% |

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
| Sao Paulo | 100.0% | 100.0% | 60.5% | 100.0% | 100.0% | 99.8% | 100.0% |
| Rio de Janeiro | 100.0% | 100.0% | 63.4% | 100.0% | 100.0% | 100.0% | 100.0% |
| Belo Horizonte | 100.0% | 100.0% | 78.0% | 100.0% | 100.0% | 96.9% | 100.0% |
| Vitoria | 100.0% | 100.0% | 67.4% | 100.0% | 100.0% | 0.0% | 100.0% |

A resposta a Q1 é positiva para os campos que estruturam o registro, mas com ressalvas relevantes. Nos registros elegíveis, o objeto, o valor estimado, as datas básicas e a unidade administrativa quase sempre estavam preenchidos. A variação concentrou-se em três pontos: o valor homologado^[Valor homologado: preço final aprovado ao término da licitação. Sua ausência costuma indicar que o processo ainda não foi concluído.], o link para o sistema de origem^[Link para o sistema de origem: endereço na internet que leva ao processo no sistema próprio do município, permitindo conferir o caso completo fora do PNCP.] e os documentos, avaliados na subamostra documental. Essa diferença importa para o controle social porque, sem o resultado final ou sem o link externo, fica mais difícil reconstituir o processo por inteiro.

Exemplos pseudoaleatórios da subamostra documental ilustram essa variação:

- Sao Paulo (`13864377000130-1-002050/2025`): data 18/11/2025; valor homologado presente; link de origem presente; 1 documento(s); objeto: REGISTRO De PREÇOS PARA O FORNECIMENTO CANULA TRAQUEOSTOMIA COM BALAO, DESCARTAVEL, ESTERIL - NR. 4,5 E SONDA ENDOTRAQUEAL, COM BALAO, RADIOPACO, D...
- Rio de Janeiro (`42498733000148-1-001315/2025`): data 24/07/2025; valor homologado presente; link de origem presente; 1 documento(s); objeto: Aquisição de Equipamento de Proteção Individual –EPI
- Belo Horizonte (`18715383000140-1-000189/2026`): data 27/03/2026; valor homologado presente; link de origem presente; 1 documento(s); objeto: O objeto da presente licitação é o registro de preços para aquisição de materiais de higiene e limpeza específicos, conforme condições e exigências...
- Vitoria (`27142058000126-1-000679/2025`): data 02/12/2025; valor homologado presente; link de origem ausente; 8 documento(s); objeto: AQUISIÇÃO DE MOBILIÁRIO E EQUIPAMENTOS DIVERSOS

| Capital | Com documentos | Amostra | Mín. | Máx. | Média |
| --- | --- | --- | --- | --- | --- |
| Sao Paulo | 100 | 100 | 1 | 1 | 1.0 |
| Rio de Janeiro | 100 | 100 | 1 | 1 | 1.0 |
| Belo Horizonte | 100 | 100 | 1 | 2 | 1.0 |
| Vitoria | 100 | 100 | 2 | 12 | 5.5 |

## Q2: consumo da API

| Etapa | Req. | Sucesso | Média | P95 | Duração | Falhas |
| --- | --- | --- | --- | --- | --- | --- |
| Coleta anual | 446 | 418 | 1.61s | 3.51s | 42min 57.4s | 28 |
| Documentos | 400 | 400 | 0.09s | 0.11s | 35.63s | 0 |
| Geração final | n/a | completa | n/a | n/a | 0.06s | 0 |
| Total observado |  |  |  |  | 43min 33.0s |  |

A resposta a Q2 é intermediária: a API funciona e entrega os dados, mas consumi-la bem exige cuidado técnico que vai além de simplesmente "acessar o endereço". Do lado positivo, a API pode ser consultada por programas, devolve os dados em formato padronizado^[**JSON**: formato de texto padronizado em que os programas trocam dados de maneira organizada, fácil de ler por outro programa.] e entrega os resultados divididos em páginas^[Paginação: quando há muitos resultados, a API não devolve tudo de uma vez; entrega em lotes (páginas) que precisam ser percorridos um a um.]. Do lado das dificuldades, a coleta de um ano inteiro só funcionou depois de uma série de precauções: anotar cada consulta e seu tempo, guardar as falhas em vez de descartá-las, quebrar o pedido em janelas de tempo menores, fazer pausas entre as páginas e conferir o tipo da resposta^[A API pode responder com uma página de erro ou de bloqueio em vez dos dados esperados. Foi preciso verificar o tipo de cada resposta para não confundir uma dessas páginas com dados válidos.] para não tratar uma mensagem de erro como se fosse dado bom.

Essa etapa reuniu 19104 registros em 418 páginas de resposta da API. Cada consulta bem-sucedida levou, em média, 1.61s; em 95% das vezes a resposta veio em até 3.51s^[Esse limite é o *percentil 95*: o tempo abaixo do qual ficaram 95% das respostas. É uma forma de descrever o caso típico sem se deixar distorcer pelos poucos atrasos maiores.], e a mais lenta chegou a 17.59s. São tempos curtos para um uso automatizado, mas a variação entre o caso típico e o pico mostra que a estabilidade não é garantida.

Na consulta aos documentos, o programa fez 400 de 400 chamadas com sucesso ao ponto de acesso de arquivos, com tempo médio de 0.09s, 0.11s no percentil 95, no máximo 1.11s e 0 falhas. Essa etapa foi mais rápida e estável que a coleta anual. No conjunto, a resposta a Q2 é favorável com ressalvas: os dados são acessíveis de forma automática e ágil, mas obtê-los com segurança exigiu controlar o ritmo das consultas, guardar as falhas e conferir a resposta — ou seja, a facilidade de consumo depende de cuidados que nem todo usuário leigo teria como adotar sozinho.

Nos dados efetivamente usados na análise, a coleta de um ano inteiro registrou 2 falha(s) de página guardada(s) nos registros de execução; mesmo assim, todas as páginas foram obtidas no final, graças a novas tentativas e a uma estratégia alternativa quando a primeira não funcionava. A consulta de documentos registrou 0 falha(s) que não foram recuperadas.

O registro detalhado de desempenho da coleta^[São arquivos que guardam, consulta por consulta, o tempo gasto e o que deu errado, permitindo auditar a execução depois.] ficou em [`data/raw/collection_request_metrics.jsonl`](https://github.com/Amorim33/analise-pncp/blob/main/data/raw/collection_request_metrics.jsonl); os erros e as tentativas malsucedidas ficam em [`data/raw/collection_errors.json`](https://github.com/Amorim33/analise-pncp/blob/main/data/raw/collection_errors.json).

O registro detalhado de desempenho da consulta de documentos ficou em [`data/raw/document_request_metrics.jsonl`](https://github.com/Amorim33/analise-pncp/blob/main/data/raw/document_request_metrics.jsonl); os erros e as tentativas malsucedidas ficam em [`data/raw/document_errors.json`](https://github.com/Amorim33/analise-pncp/blob/main/data/raw/document_errors.json).

## Constatações empíricas

- Na amostra candidata de Sao Paulo, 98.9% dos registros elegiveis ficaram fora do CNPJ matriz; nas demais capitais analisadas, os registros por CNPJ matriz concentraram 100% dos candidatos coletados.
- Sao Paulo apresentou 67 CNPJs distintos no recorte elegivel, enquanto Rio de Janeiro, Belo Horizonte e Vitoria apareceram com um CNPJ cada no recorte por matriz.
- Vitoria teve documentos vinculados em todos os itens da subamostra documental, mas nenhum dos registros elegiveis trouxe `linkSistemaOrigem`, o que reduz a rastreabilidade para o sistema de origem.
- O valor homologado apareceu com menor completude em Sao Paulo (60.5%), indicando que parte dos registros estava em fase anterior ao resultado ou sem homologacao registrada no recorte.
- A quantidade de documentos anexados variou de forma relevante: em Vitoria, um item da amostra chegou a 12 documentos, enquanto outros municipios tiveram padrao mais concentrado.

# Conclusões

A análise indica que o PNCP é uma infraestrutura importante de governo aberto: ele centraliza registros, expõe campos padronizados, oferece documentos e permite automação por API. Esses elementos fortalecem a transparência formal e criam condições para controle social.

Ao mesmo tempo, a comparação mostra que abertura não é sinônimo automático de inteligibilidade. A fragmentação de CNPJs em São Paulo torna a busca mais complexa e pode subestimar a atividade contratual municipal quando o pesquisador consulta apenas o CNPJ matriz. A contribuição do trabalho está em mostrar que a avaliação de governo aberto deve observar também a arquitetura institucional dos dados.

Como conclusão regional exploratória, as capitais do Sudeste analisadas apresentam boa disponibilidade básica de dados e documentos no PNCP, mas diferem na forma de organização dos registros. A agenda de melhoria passa por documentação mais clara dos CNPJs e unidades, maior preenchimento dos links para os sistemas de origem e mecanismos que facilitem ao cidadão reconstruir o conjunto de órgãos vinculados a cada prefeitura.

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

A pesquisa é exploratória e não representa todos os municípios do Sudeste. A API de consulta por publicação limita cada requisição a janelas de até 365 dias; por isso, o recorte usa a maior janela aceita em uma consulta reprodutível. Além disso, os documentos vinculados foram analisados a partir de uma subamostra sorteada de forma reproduzível, e não a totalidade dos documentos. Por fim, os resultados podem mudar com novas publicações, retificações ou alterações na API do PNCP.
