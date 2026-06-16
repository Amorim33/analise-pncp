---
title: "Portal Nacional de Contratações Públicas e governo aberto: uma análise exploratória das capitais do Sudeste"
subtitle: "Transparência formal, dados abertos e fragmentação institucional"
author:
  - "PREENCHER_NOME"
date: "2026-07-01"
lang: pt-BR
course: "Governo Aberto"
instructor: "Jorge Machado"
institution: "Universidade de São Paulo"
---

# Introdução

Este trabalho analisa o Portal Nacional de Contratações Públicas (PNCP) como infraestrutura de governo aberto nas capitais do Sudeste brasileiro. A pergunta de pesquisa é: em que medida a publicação de contratações no PNCP favorece transparência, reutilização de dados e controle social nas prefeituras de São Paulo, Rio de Janeiro, Belo Horizonte e Vitória?

O tema dialoga com a disciplina Governo Aberto porque combina acesso à informação, padrões tecnológicos, dados abertos e accountability. A própria disciplina orienta que o trabalho articule problema, objetivos, método e conclusões, com atenção à estrutura textual e às normas de citação [@curso2026]. O PNCP é especialmente relevante porque a Lei nº 14.133/2021 o institui como ambiente nacional de divulgação de contratações públicas [@lei14133].

O argumento central é que o PNCP amplia a transparência formal ao centralizar metadados, documentos e links de origem, mas a efetividade como governo aberto depende da completude dos registros e da capacidade de reconstituir a organização administrativa de cada prefeitura. O caso de São Paulo mostra essa tensão com mais nitidez: grande parte dos registros municipais aparece fora do CNPJ matriz do município.

# Objetivos e método

O objetivo geral é avaliar, de forma exploratória, como o PNCP expressa princípios de governo aberto nas contratações das capitais do Sudeste. Os objetivos específicos são: comparar volume e concentração institucional dos registros, verificar a completude de campos essenciais, observar a presença de documentos e discutir a fragmentação de CNPJs em São Paulo.

O recorte empírico considera pregões eletrônicos, modalidade 6 no PNCP, publicados entre 2026-01-01 e 2026-05-31. Foram usados os CNPJs matriz das prefeituras de Rio de Janeiro, Belo Horizonte e Vitória. Para São Paulo, combinou-se o CNPJ matriz com uma varredura por UF e código IBGE, filtrando entidades municipais executivas.

| Capital | Fonte de coleta | Registros brutos | Limite |
| --- | --- | --- | --- |
| Sao Paulo | matrix_cnpj | 6 |  |
| Sao Paulo | municipality_scan | 250 | 5 |
| Rio de Janeiro | matrix_cnpj | 347 |  |
| Belo Horizonte | matrix_cnpj | 90 |  |
| Vitoria | matrix_cnpj | 97 |  |

A amostra final selecionou até dez contratações por capital, por sorteio pseudoaleatório reprodutível após ordenação por `numeroControlePNCP`. A semente usada foi 20260608. A opção por amostra fixa evita que capitais com mais registros dominem a interpretação.

# Referencial teórico

Governo aberto costuma ser descrito como um arranjo que combina transparência, participação social, colaboração e prestação de contas. A Open Government Partnership associa o tema a compromissos de abertura, integridade pública e participação cidadã [@ogpDeclaration]. A OCDE também define governo aberto como uma cultura de governança que promove princípios de transparência, integridade, accountability e participação das partes interessadas [@oecd2017].

Dados abertos são uma dimensão operacional desse debate. Para que a publicação seja útil, não basta disponibilizar informação em páginas isoladas: é necessário permitir acesso, reuso, padronização e combinação com outras bases [@w3cManualDadosAbertos]. A Lei de Acesso à Informação também reforça a publicidade como regra e o sigilo como exceção [@lei12527]. Assim, transparência pública deve ser avaliada não apenas pela existência de dados, mas por sua usabilidade para fiscalização e pesquisa.

No caso brasileiro, o PNCP constitui uma infraestrutura relevante para esse tipo de análise, pois centraliza informações e documentos de contratações públicas [@pncpPortal]. A existência de API e de dados consultáveis amplia o potencial de reutilização por cidadãos, pesquisadores e jornalistas [@pncpDadosAbertos; @pncpApiConsulta].

# Desenvolvimento e análise

## Visão comparativa

| Capital | Candidatos | Amostra | CNPJs distintos | Registros na matriz | Participação da matriz |
| --- | --- | --- | --- | --- | --- |
| Sao Paulo | 61 | 10 | 10 | 6 | 9.8% |
| Rio de Janeiro | 347 | 10 | 1 | 347 | 100.0% |
| Belo Horizonte | 90 | 10 | 1 | 90 | 100.0% |
| Vitoria | 97 | 10 | 1 | 97 | 100.0% |

A primeira diferença relevante está na concentração institucional. Rio de Janeiro, Belo Horizonte e Vitória aparecem concentradas no CNPJ matriz no recorte adotado. São Paulo, por outro lado, apresenta múltiplos CNPJs municipais executivos associados a unidades como fundo municipal, hospital, companhia de engenharia de tráfego, secretaria e subprefeitura.

## Fragmentação em São Paulo

| Métrica | Valor |
| --- | --- |
| CNPJ matriz | 46395000000139 |
| Registros candidatos | 61 |
| Registros no CNPJ matriz | 6 |
| Registros fora do CNPJ matriz | 55 |
| Participação fora da matriz | 90.2% |
| CNPJs distintos | 10 |
| CNPJs fora da matriz | 9 |

Esse resultado é substantivo para governo aberto. Uma consulta limitada ao CNPJ matriz de São Paulo recuperaria apenas uma fração dos registros elegíveis. Portanto, a transparência formal do PNCP convive com uma barreira de reconstrução institucional: o cidadão precisa saber que a prefeitura pode publicar contratações por diferentes CNPJs municipais.

## Completude e rastreabilidade

| Capital | Campo | Presentes | Amostra | Percentual |
| --- | --- | --- | --- | --- |
| Sao Paulo | Valor homologado | 7 | 10 | 70.0% |
| Sao Paulo | Link de origem | 10 | 10 | 100.0% |
| Sao Paulo | Documentos | 10 | 10 | 100.0% |
| Rio de Janeiro | Valor homologado | 6 | 10 | 60.0% |
| Rio de Janeiro | Link de origem | 10 | 10 | 100.0% |
| Rio de Janeiro | Documentos | 10 | 10 | 100.0% |
| Belo Horizonte | Valor homologado | 7 | 10 | 70.0% |
| Belo Horizonte | Link de origem | 9 | 10 | 90.0% |
| Belo Horizonte | Documentos | 10 | 10 | 100.0% |
| Vitoria | Valor homologado | 3 | 10 | 30.0% |
| Vitoria | Link de origem | 0 | 10 | 0.0% |
| Vitoria | Documentos | 10 | 10 | 100.0% |

Em todos os municípios da amostra, objeto, datas básicas, unidade administrativa e documentos estiveram amplamente disponíveis. A principal variação apareceu em valor homologado e link do sistema de origem. Vitória, por exemplo, teve documentos em todos os itens amostrados, mas nenhum dos dez registros trouxe `linkSistemaOrigem`, o que reduz a rastreabilidade para o ambiente de origem.

| Capital | Com documentos | Amostra | Mín. | Máx. | Média |
| --- | --- | --- | --- | --- | --- |
| Sao Paulo | 10 | 10 | 1 | 1 | 1.0 |
| Rio de Janeiro | 10 | 10 | 1 | 1 | 1.0 |
| Belo Horizonte | 10 | 10 | 1 | 1 | 1.0 |
| Vitoria | 10 | 10 | 2 | 12 | 3.8 |

## Constatações empíricas

- Na amostra candidata de Sao Paulo, 90.2% dos registros elegiveis ficaram fora do CNPJ matriz; nas demais capitais analisadas, os registros por CNPJ matriz concentraram 100% dos candidatos coletados.
- Sao Paulo apresentou 10 CNPJs distintos no recorte elegivel, enquanto Rio de Janeiro, Belo Horizonte e Vitoria apareceram com um CNPJ cada no recorte por matriz.
- Vitoria teve documentos vinculados em todos os itens da amostra, mas nenhum dos 10 registros amostrados trouxe `linkSistemaOrigem`, o que reduz a rastreabilidade para o sistema de origem.
- O valor homologado apareceu com menor completude em Vitoria (30.0%), indicando que parte dos registros estava em fase anterior ao resultado ou sem homologacao registrada no recorte.
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

- Controle PNCP: `13864377000130-1-000007/2026`
- CNPJ/órgão: `13864377000130` — FUNDO MUNICIPAL DE SAUDE - FMS
- Unidade: PMSP - SECRETARIA MUNICIPAL DE SAÚDE
- Valor estimado: 863090.8
- Valor homologado: 633080.0
- Situação: Divulgada no PNCP
- Documentos listados no exemplo: 1
- Objeto: REGISTRO De PREÇOS OBJETIVANDO O FORNECIMENTO DE MATERIAIS DE OPME - SISTEMA DE PLACA E PARAFUSOPARA MÃO COM ENTREGA EM CONSIGNAÇÃO E COMODATO DE INSTRUMENTAIS E EQUIPAMENTOS, NECESSÁRIOS PARA O ATENDIMENTO DE CIRURGIAS NA ESPECIALIDADE DE ORTOPEDIA, A SEREM UTILIZADOS NAS UNIDADES HOSPITALARES PERTENCENTES À SECRETARIA MUNICIPAL DA SAÚDE DE SP, PARA O PERÍODO DE 12(DOZE) MESES.

## Sao Paulo - exemplo no CNPJ matriz

- Controle PNCP: `46395000000139-1-000028/2026`
- CNPJ/órgão: `46395000000139` — MUNICIPIO DE SAO PAULO
- Unidade: PMSP - SECRETARIA DO GOVERNO MUNICIPAL
- Valor estimado: 4652861.35
- Valor homologado: 4652499.96
- Situação: Divulgada no PNCP
- Documentos listados no exemplo: 1
- Objeto: Contratação de empresa especializada na prestação de serviços de controle de acesso do Edifício Conde Matarazzo, abrangendo a cobertura efetiva das portarias, a disponibilização de equipamentos de informática, a emissão de crachás e películas de identificação, bem como a manutenção preventiva e corretiva dos módulos de passagem, utilizando-se o software de propriedade da CONTRATANTE, com o fornecimento de peças necessárias. O objetivo é assegu...

## Rio de Janeiro

- Controle PNCP: `42498733000148-1-000127/2026`
- CNPJ/órgão: `42498733000148` — MUNICIPIO DE RIO DE JANEIRO
- Unidade: PREFEITURA MUNICIPAL DO RIO DE JANEIRO - RJ
- Valor estimado: 99005.6
- Valor homologado: 85452.38
- Situação: Divulgada no PNCP
- Documentos listados no exemplo: 1
- Objeto: Registro de Preços para Aquisição de Materiais de Instalações Elétricas (C), para manutenção rotineira, a serem utilizados nas unidades físicas do Sistema BRT da MOBI-Rio.

## Belo Horizonte

- Controle PNCP: `18715383000140-1-000178/2026`
- CNPJ/órgão: `18715383000140` — MUNICIPIO DE BELO HORIZONTE
- Unidade: SECRETARIA MUNICIPAL DE EDUCAÇÃO
- Valor estimado: 111600.0
- Valor homologado: 72000.0
- Situação: Divulgada no PNCP
- Documentos listados no exemplo: 1
- Objeto: FORNECIMENTO DE AGUA MINERAL NATURAL EM GARRAFAO COM 20 LITROS, INCLUINDO O EMPRESTIMO A TITULO DE COMODATO DE GARRAFAO COM CAPACIDADE PARA 20 LITROSVASILHAME, DESTINADOS AO ABASTECIMENTO DA SEDE DA SECRETARIA MUNICIPAL DE EDUCACAO ? SMED E GERENCIA REGIONAL DE EDUCACAO - BARREIRO , NOS TERMOS DA TABELA ABAIXO E CONFORME CONDICOES E EXIGENCIAS ESTABELECIDAS NESTE INSTRUMENTO.

## Vitoria

- Controle PNCP: `27142058000126-1-000034/2026`
- CNPJ/órgão: `27142058000126` — MUNICIPIO DE VITORIA
- Unidade: PREFEITURA MUNICIPAL DE VITORIA
- Valor estimado: 669364.4
- Valor homologado: não informado
- Situação: Divulgada no PNCP
- Documentos listados no exemplo: 2
- Objeto: FORNECIMENTO DE ALIMENTOS (DESJEJUM, KIT LANCHE E MARMITEX).


# Apêndice B: declaração de uso de IA

Este trabalho utilizou ferramentas de inteligência artificial generativa para apoio à programação do pipeline de coleta e análise, organização dos resultados, revisão textual e geração inicial do relatório. A seleção do tema, a validação das fontes, a interpretação dos resultados e a versão final são de responsabilidade do(s) autor(es).

# Apêndice C: limitações metodológicas

A pesquisa é exploratória e não representa todos os municípios do Sudeste. A varredura municipal de São Paulo foi limitada operacionalmente a cinco páginas da API para manter o pipeline reprodutível em tempo razoável. Além disso, os resultados podem mudar com novas publicações, retificações ou alterações na API do PNCP.
