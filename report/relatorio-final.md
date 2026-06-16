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
abstract: "Relatório acadêmico exploratório sobre transparência, reutilização de dados e fragmentação institucional em contratações públicas municipais publicadas no PNCP."
---

# Introdução

Este trabalho analisa o Portal Nacional de Contratações Públicas (PNCP) como infraestrutura de governo aberto nas capitais do Sudeste brasileiro. A pergunta de pesquisa é: em que medida a publicação de contratações no PNCP favorece transparência, reutilização de dados e controle social nas prefeituras das capitais dos estados do sudeste brasileiro (São Paulo, Rio de Janeiro, Belo Horizonte e Vitória)?

O tema dialoga com a disciplina Governo Aberto porque combina acesso à informação, padrões tecnológicos, dados abertos e accountability. A própria disciplina orienta que o trabalho articule problema, objetivos, método e conclusões, com atenção à estrutura textual e às normas de citação [@curso2026]. O PNCP é especialmente relevante porque a Lei nº 14.133/2021 o institui como ambiente nacional de divulgação de contratações públicas [@lei14133].

O argumento central é que o PNCP amplia a transparência formal ao centralizar metadados, documentos e links de origem, mas a efetividade como governo aberto depende da completude dos registros e da capacidade de reconstituir a organização administrativa de cada prefeitura. O caso de São Paulo mostra essa tensão com mais nitidez: grande parte dos registros municipais aparece fora do CNPJ matriz do município.

# Objetivos e método

O objetivo geral é avaliar, de forma exploratória, como o PNCP expressa princípios de governo aberto nas contratações das capitais do Sudeste. Os objetivos específicos são: comparar volume e concentração institucional dos registros, verificar a completude de campos essenciais, observar a presença de documentos e discutir a fragmentação de CNPJs em São Paulo.

O recorte empírico considera pregões eletrônicos, modalidade 6 no PNCP, publicados entre 15/06/2025 a 15/06/2026. Foram usados os CNPJs matriz das prefeituras de Rio de Janeiro, Belo Horizonte e Vitória. Para São Paulo, combinou-se o CNPJ matriz com uma varredura por UF e código IBGE, filtrando entidades municipais executivas.

| Capital | Fonte | Registros | Páginas | Total | Limite |
| --- | --- | --- | --- | --- | --- |
| Sao Paulo | matriz | 30 | 12 | 12 |  |
| Sao Paulo | município | 17654 | 359 | 359 | todas |
| Rio de Janeiro | matriz | 896 | 23 | 23 |  |
| Belo Horizonte | matriz | 291 | 12 | 12 |  |
| Vitoria | matriz | 234 | 12 | 12 |  |

A amostra principal inclui todos os registros elegíveis no período, após deduplicação por `numeroControlePNCP`. Para a análise de documentos, foi usada subamostra determinística de até 100 registros por capital. A semente usada foi 20260608.

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

## Completude e rastreabilidade

| Capital | Campo | Presentes | Amostra | Percentual |
| --- | --- | --- | --- | --- |
| Sao Paulo | Valor homologado | 1608 | 2662 | 60.4% |
| Sao Paulo | Link de origem | 2658 | 2662 | 99.8% |
| Sao Paulo | Documentos | 100 | 100 | 100.0% |
| Rio de Janeiro | Valor homologado | 563 | 896 | 62.8% |
| Rio de Janeiro | Link de origem | 896 | 896 | 100.0% |
| Rio de Janeiro | Documentos | 100 | 100 | 100.0% |
| Belo Horizonte | Valor homologado | 227 | 291 | 78.0% |
| Belo Horizonte | Link de origem | 282 | 291 | 96.9% |
| Belo Horizonte | Documentos | 100 | 100 | 100.0% |
| Vitoria | Valor homologado | 156 | 234 | 66.7% |
| Vitoria | Link de origem | 0 | 234 | 0.0% |
| Vitoria | Documentos | 100 | 100 | 100.0% |

Nos registros elegíveis, objeto, datas básicas e unidade administrativa estiveram amplamente disponíveis; documentos foram avaliados na subamostra documental. A principal variação apareceu em valor homologado e link do sistema de origem. Vitória, por exemplo, teve documentos nos itens da subamostra documental, mas nenhum registro elegível trouxe `linkSistemaOrigem`, o que reduz a rastreabilidade para o ambiente de origem.

| Capital | Com documentos | Amostra | Mín. | Máx. | Média |
| --- | --- | --- | --- | --- | --- |
| Sao Paulo | 100 | 100 | 1 | 1 | 1.0 |
| Rio de Janeiro | 100 | 100 | 1 | 1 | 1.0 |
| Belo Horizonte | 100 | 100 | 1 | 2 | 1.0 |
| Vitoria | 100 | 100 | 1 | 12 | 5.3 |

## Constatações empíricas

- Na amostra candidata de Sao Paulo, 98.9% dos registros elegiveis ficaram fora do CNPJ matriz; nas demais capitais analisadas, os registros por CNPJ matriz concentraram 100% dos candidatos coletados.
- Sao Paulo apresentou 67 CNPJs distintos no recorte elegivel, enquanto Rio de Janeiro, Belo Horizonte e Vitoria apareceram com um CNPJ cada no recorte por matriz.
- Vitoria teve documentos vinculados em todos os itens da subamostra documental, mas nenhum dos registros elegiveis trouxe `linkSistemaOrigem`, o que reduz a rastreabilidade para o sistema de origem.
- O valor homologado apareceu com menor completude em Sao Paulo (60.4%), indicando que parte dos registros estava em fase anterior ao resultado ou sem homologacao registrada no recorte.
- A quantidade de documentos anexados variou de forma relevante: em Vitoria, um item da amostra chegou a 12 documentos, enquanto outros municipios tiveram padrao mais concentrado.

## Exemplos de registros

Os exemplos completos foram deslocados para o Apêndice A. No corpo do texto, basta notar que um registro da Secretaria Municipal de Saúde de São Paulo retorna CNPJ do Fundo Municipal de Saúde, unidade `PMSP - SECRETARIA MUNICIPAL DE SAÚDE`, objeto de aquisição hospitalar e documento de edital. Já o exemplo no CNPJ matriz retorna `MUNICIPIO DE SAO PAULO` e unidade da Secretaria do Governo Municipal. Essa diferença concreta sustenta a leitura de fragmentação institucional.

# Conclusões

A análise indica que o PNCP é uma infraestrutura importante de governo aberto: ele centraliza registros, expõe campos padronizados, oferece documentos e permite automação por API. Esses elementos fortalecem a transparência formal e criam condições para controle social.

Ao mesmo tempo, a comparação mostra que abertura não é sinônimo automático de inteligibilidade. A fragmentação de CNPJs em São Paulo torna a busca mais complexa e pode subestimar a atividade contratual municipal quando o pesquisador consulta apenas o CNPJ matriz. A contribuição do trabalho está em mostrar que a avaliação de governo aberto deve observar também a arquitetura institucional dos dados.

Como conclusão regional exploratória, as capitais do Sudeste analisadas apresentam boa disponibilidade básica de dados e documentos no PNCP, mas diferem na forma de organização dos registros. A agenda de melhoria passa por documentação mais clara dos CNPJs/unidades, maior completude de links de origem e mecanismos que facilitem ao cidadão reconstruir o universo de órgãos vinculados a cada prefeitura.

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
- Objeto: CONTRATAÇÃO DE EMPRESA DO RAMO PARA A AQUISIÇÃO E INSTALAÇÃO DE PARQUE INFANTIL, DEVIDAMENTE CERTIFICADO POR ÓRGÃO COMPETENTE, PARA ATENDER AS NECESSIDADES DO FUNDO MUNICIPAL DE EDUCAÇÃO/FME, CONFORME EMENDA PARLAMENTAR Nº 1299.2/2025, PROCESSO Nº 202500005022377.

## Sao Paulo - exemplo no CNPJ matriz

- Controle PNCP: `46395000000139-1-000007/2026`
- CNPJ/órgão: `46395000000139` — MUNICIPIO DE SAO PAULO
- Unidade: PMSP - SECRETARIA DO GOVERNO MUNICIPAL
- Valor estimado: 62640.7
- Valor homologado: 42066.57
- Situação: Divulgada no PNCP
- Documentos listados no exemplo: 0
- Objeto: Aquisição de materiais de construção, abrangendo itens das linhas hidráulica, elétrica, ferragens, pintura, alvenaria, acabamentos e correlatos, conforme as especificações, quantidades e condições estabelecidas neste Termo de Referência considerando AUSÊNCIA de código específico para cada item no www.gov.br/compras, solicitamos que para a formação da proposta de preços e o registro no sistema, o licitante baseie-se EXCLUSIVAMENTE, nas informaç...

## Rio de Janeiro

- Controle PNCP: `42498733000148-1-000104/2026`
- CNPJ/órgão: `42498733000148` — MUNICIPIO DE RIO DE JANEIRO
- Unidade: PREFEITURA MUNICIPAL DO RIO DE JANEIRO - RJ
- Valor estimado: 0.0
- Valor homologado: não informado
- Situação: Divulgada no PNCP
- Documentos listados no exemplo: 0
- Objeto: CoNTRATAÇÃO DE EMPRESA ESPECIALIZADA PARA PRESTAÇÃO DE SERVIÇOS DE PLANEJAMENTO, ORGANIZAÇÃO, EXECUÇÃO, ACOMPANHAMENTO, FORNECIMENTO DE BENS E INSUMOS, INFRAESTRUTURA E APOIO LOGÍSTICO, VISANDO A REALIZAÇÃO DO BAILE DA CINELÂNDIA E DESFILES DA AVENIDA CHILE, CARNAVAL DO RIO 2026

## Belo Horizonte

- Controle PNCP: `18715383000140-1-000024/2026`
- CNPJ/órgão: `18715383000140` — MUNICIPIO DE BELO HORIZONTE
- Unidade: PREF.MUN.DE BELO HORIZONTE
- Valor estimado: 3585413.35
- Valor homologado: 1969468.81
- Situação: Divulgada no PNCP
- Documentos listados no exemplo: 0
- Objeto: O objeto da presente licitação é a aquisição de COLETES DE PROTEÇÃO BALÍSTICA FLEXÍVEL, PARA USO POLICIAL, NÍVEL DE PROTEÇÃO III-A, COM CAPA EXTERNA TIPO MODULAR (COM CAPA SOBRESSALENTE TIPO MODULAR), com a finalidade de atender atividades operacionais da Guarda Civil Municipal de Belo Horizonte, conforme condições e exigências estabelecidas neste Edital, Termo de Referência e demais anexos.

## Vitoria

- Controle PNCP: `27142058000126-1-000005/2026`
- CNPJ/órgão: `27142058000126` — MUNICIPIO DE VITORIA
- Unidade: PREFEITURA MUNICIPAL DE VITORIA
- Valor estimado: 31435.32
- Valor homologado: 28209.6
- Situação: Divulgada no PNCP
- Documentos listados no exemplo: 0
- Objeto: AQUISIÇÃO DE CLIMATIZADORES DE AR


# Apêndice B: declaração de uso de IA

Este trabalho utilizou ferramentas de inteligência artificial generativa para apoio à programação do pipeline de coleta e análise, organização dos resultados, revisão textual e geração inicial do relatório. A seleção do tema, a validação das fontes, a interpretação dos resultados e a versão final são de responsabilidade do(s) autor(es).

# Apêndice C: limitações metodológicas

A pesquisa é exploratória e não representa todos os municípios do Sudeste. A API de consulta por publicação limita cada requisição a janelas de até 365 dias; por isso, o recorte usa a maior janela aceita em uma consulta reprodutível. Além disso, documentos vinculados foram analisados por subamostra determinística, e os resultados podem mudar com novas publicações, retificações ou alterações na API do PNCP.
