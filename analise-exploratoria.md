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

## Exemplos de registros retornados pela API

Os exemplos abaixo usam um subconjunto dos campos retornados pela API do PNCP. Eles mostram como a informacao chega para a analise: identificador PNCP, orgao, unidade, objeto, valores, situacao, link de origem e documentos vinculados.

### Sao Paulo - exemplo fora do CNPJ matriz

```json
{
  "documentos": [
    {
      "tipoDocumentoNome": "Edital",
      "titulo": "92500305900032026000",
      "url": "https://pncp.gov.br/pncp-api/v1/orgaos/13864377000130/compras/2026/7/arquivos/1"
    }
  ],
  "linkSistemaOrigem": "https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/landing?destino=acompanhamento-compra&compra=92500305900032026",
  "numeroControlePNCP": "13864377000130-1-000007/2026",
  "objetoCompra": "REGISTRO De PREÇOS OBJETIVANDO O FORNECIMENTO DE MATERIAIS DE OPME - SISTEMA DE PLACA E PARAFUSOPARA MÃO  COM ENTREGA EM CONSIGNAÇÃO E COMODATO DE INSTRUMENTAIS E EQUIPAMENTOS, NECESSÁRIOS PARA O ATENDIMENTO DE CIRURGIAS NA ESPECIALIDADE DE ORTOPEDIA, A SEREM UTILIZADOS NAS UNIDADES HOSPITALARES PERTENCENTES À SECRETARIA MUNICIPAL DA SAÚDE DE SP, PARA O PERÍODO DE 12(DOZE) MESES.",
  "orgaoEntidade": {
    "cnpj": "13864377000130",
    "esferaId": "M",
    "poderId": "E",
    "razaoSocial": "FUNDO MUNICIPAL DE SAUDE - FMS"
  },
  "situacaoCompraNome": "Divulgada no PNCP",
  "unidadeOrgao": {
    "codigoIbge": "3550308",
    "codigoUnidade": "925003",
    "municipioNome": "São Paulo",
    "nomeUnidade": "PMSP - SECRETARIA MUNICIPAL DE SAÚDE",
    "ufNome": "São Paulo",
    "ufSigla": "SP"
  },
  "valorTotalEstimado": 863090.8,
  "valorTotalHomologado": 633080.0
}
```
### Sao Paulo - exemplo no CNPJ matriz

```json
{
  "documentos": [
    {
      "tipoDocumentoNome": "Edital",
      "titulo": "92505605900012026000",
      "url": "https://pncp.gov.br/pncp-api/v1/orgaos/46395000000139/compras/2026/28/arquivos/1"
    }
  ],
  "linkSistemaOrigem": "https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/landing?destino=acompanhamento-compra&compra=92505605900012026",
  "numeroControlePNCP": "46395000000139-1-000028/2026",
  "objetoCompra": "Contratação de empresa especializada na prestação de serviços de controle de acesso do Edifício Conde Matarazzo, abrangendo a cobertura efetiva das portarias, a disponibilização de equipamentos de informática, a emissão de crachás e películas de identificação, bem como a manutenção preventiva e corretiva dos módulos de passagem, utilizando-se o software de propriedade da CONTRATANTE, com o fornecimento de peças necessárias. O objetivo é assegurar o gerenciamento ",
  "orgaoEntidade": {
    "cnpj": "46395000000139",
    "esferaId": "M",
    "poderId": "E",
    "razaoSocial": "MUNICIPIO DE SAO PAULO"
  },
  "situacaoCompraNome": "Divulgada no PNCP",
  "unidadeOrgao": {
    "codigoIbge": "3550308",
    "codigoUnidade": "925056",
    "municipioNome": "São Paulo",
    "nomeUnidade": "PMSP - SECRETARIA DO GOVERNO MUNICIPAL",
    "ufNome": "São Paulo",
    "ufSigla": "SP"
  },
  "valorTotalEstimado": 4652861.35,
  "valorTotalHomologado": 4652499.96
}
```
### Rio de Janeiro

```json
{
  "documentos": [
    {
      "tipoDocumentoNome": "Edital",
      "titulo": "98600105900142026000",
      "url": "https://pncp.gov.br/pncp-api/v1/orgaos/42498733000148/compras/2026/127/arquivos/1"
    }
  ],
  "linkSistemaOrigem": "https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/landing?destino=acompanhamento-compra&compra=98600105900142026",
  "numeroControlePNCP": "42498733000148-1-000127/2026",
  "objetoCompra": "Registro de Preços para Aquisição de Materiais de Instalações Elétricas (C), para manutenção rotineira, a serem utilizados nas unidades físicas do Sistema BRT da MOBI-Rio.",
  "orgaoEntidade": {
    "cnpj": "42498733000148",
    "esferaId": "M",
    "poderId": "N",
    "razaoSocial": "MUNICIPIO DE RIO DE JANEIRO"
  },
  "situacaoCompraNome": "Divulgada no PNCP",
  "unidadeOrgao": {
    "codigoIbge": "3304557",
    "codigoUnidade": "986001",
    "municipioNome": "Rio de Janeiro",
    "nomeUnidade": "PREFEITURA MUNICIPAL DO RIO DE JANEIRO - RJ",
    "ufNome": "Rio de Janeiro",
    "ufSigla": "RJ"
  },
  "valorTotalEstimado": 99005.6,
  "valorTotalHomologado": 85452.38
}
```
### Belo Horizonte

```json
{
  "documentos": [
    {
      "tipoDocumentoNome": "Edital",
      "titulo": "EDITAL",
      "url": "https://pncp.gov.br/pncp-api/v1/orgaos/18715383000140/compras/2026/178/arquivos/1"
    }
  ],
  "linkSistemaOrigem": "",
  "numeroControlePNCP": "18715383000140-1-000178/2026",
  "objetoCompra": "FORNECIMENTO DE AGUA MINERAL NATURAL EM GARRAFAO COM 20 LITROS, INCLUINDO O EMPRESTIMO A TITULO DE COMODATO DE GARRAFAO COM CAPACIDADE PARA 20 LITROSVASILHAME, DESTINADOS AO ABASTECIMENTO DA SEDE DA SECRETARIA MUNICIPAL DE EDUCACAO ? SMED E GERENCIA REGIONAL DE EDUCACAO - BARREIRO , NOS TERMOS DA TABELA ABAIXO E CONFORME CONDICOES E EXIGENCIAS ESTABELECIDAS NESTE INSTRUMENTO.",
  "orgaoEntidade": {
    "cnpj": "18715383000140",
    "esferaId": "M",
    "poderId": "N",
    "razaoSocial": "MUNICIPIO DE BELO HORIZONTE"
  },
  "situacaoCompraNome": "Divulgada no PNCP",
  "unidadeOrgao": {
    "codigoIbge": "3106200",
    "codigoUnidade": "2200",
    "municipioNome": "Belo Horizonte",
    "nomeUnidade": "SECRETARIA MUNICIPAL DE EDUCAÇÃO",
    "ufNome": "Minas Gerais",
    "ufSigla": "MG"
  },
  "valorTotalEstimado": 111600.0,
  "valorTotalHomologado": 72000.0
}
```
### Vitoria

```json
{
  "documentos": [
    {
      "tipoDocumentoNome": "Edital",
      "titulo": "EDITAL2026018",
      "url": "https://pncp.gov.br/pncp-api/v1/orgaos/27142058000126/compras/2026/34/arquivos/1"
    },
    {
      "tipoDocumentoNome": "Termo de Referência",
      "titulo": "TERMO DE REFERENCIA",
      "url": "https://pncp.gov.br/pncp-api/v1/orgaos/27142058000126/compras/2026/34/arquivos/2"
    }
  ],
  "linkSistemaOrigem": null,
  "numeroControlePNCP": "27142058000126-1-000034/2026",
  "objetoCompra": "FORNECIMENTO DE ALIMENTOS (DESJEJUM, KIT LANCHE E MARMITEX).",
  "orgaoEntidade": {
    "cnpj": "27142058000126",
    "esferaId": "M",
    "poderId": "N",
    "razaoSocial": "MUNICIPIO DE VITORIA"
  },
  "situacaoCompraNome": "Divulgada no PNCP",
  "unidadeOrgao": {
    "codigoIbge": "3205309",
    "codigoUnidade": "1",
    "municipioNome": "Vitória",
    "nomeUnidade": "PREFEITURA MUNICIPAL DE VITORIA",
    "ufNome": "Espírito Santo",
    "ufSigla": "ES"
  },
  "valorTotalEstimado": 669364.4,
  "valorTotalHomologado": null
}
```

## Amostra

| Capital | Registros candidatos | Amostra | CNPJs distintos | Registros no CNPJ matriz | Participacao da matriz |
| --- | --- | --- | --- | --- | --- |
| Sao Paulo | 61 | 10 | 10 | 6 | 9.8% |
| Rio de Janeiro | 347 | 10 | 1 | 347 | 100.0% |
| Belo Horizonte | 90 | 10 | 1 | 90 | 100.0% |
| Vitoria | 97 | 10 | 1 | 97 | 100.0% |

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
| Vitoria | 27142058000126-1-000238/2026 | 27142058000126 | MUNICIPIO DE VITORIA | 4 |
| Vitoria | 27142058000126-1-000268/2026 | 27142058000126 | MUNICIPIO DE VITORIA | 2 |
| Vitoria | 27142058000126-1-000270/2026 | 27142058000126 | MUNICIPIO DE VITORIA | 2 |

## Constatações adicionais

- Na amostra candidata de Sao Paulo, 90.2% dos registros elegiveis ficaram fora do CNPJ matriz; nas demais capitais analisadas, os registros por CNPJ matriz concentraram 100% dos candidatos coletados.
- Sao Paulo apresentou 10 CNPJs distintos no recorte elegivel, enquanto Rio de Janeiro, Belo Horizonte e Vitoria apareceram com um CNPJ cada no recorte por matriz.
- Vitoria teve documentos vinculados em todos os itens da amostra, mas nenhum dos 10 registros amostrados trouxe `linkSistemaOrigem`, o que reduz a rastreabilidade para o sistema de origem.
- O valor homologado apareceu com menor completude em Vitoria (30.0%), indicando que parte dos registros estava em fase anterior ao resultado ou sem homologacao registrada no recorte.
- A quantidade de documentos anexados variou de forma relevante: em Vitoria, um item da amostra chegou a 12 documentos, enquanto outros municipios tiveram padrao mais concentrado.

## Fragmentacao de CNPJs em Sao Paulo

| Metrica | Valor |
| --- | --- |
| CNPJ matriz | 46395000000139 |
| Registros candidatos de Sao Paulo | 61 |
| Registros no CNPJ matriz | 6 |
| Registros fora do CNPJ matriz | 55 |
| Participacao fora do CNPJ matriz | 90.2% |
| CNPJs distintos no recorte | 10 |
| CNPJs distintos fora da matriz | 9 |

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

Exemplos de registros fora do CNPJ matriz reforcam que a fragmentacao nao e apenas nominal: diferentes CNPJs publicam objetos e unidades administrativas proprias no PNCP.

| CNPJ | Orgao | Controle PNCP | Unidade | Objeto |
| --- | --- | --- | --- | --- |
| 13864377000130 | FUNDO MUNICIPAL DE SAUDE - FMS | 13864377000130-1-000006/2026 | PMSP - SECRETARIA MUNICIPAL DE SAÚDE | REGISTRO de PREÇOS PARA O FORNECIMENTO DE FRASCO, COLETOR, P/ BRONCOSCOPIA, DESCARTAVEL, ESTERIL, 120 ML |
| 47902648000117 | PMSP - COMPANHIA DE ENGENHARIA DE TRÁFEGO | 47902648000117-1-000049/2025 | PMSP - COMPANHIA DE ENGENHARIA DE TRÁFEGO-CET | Fornecimento de pneus, câmaras de ar e protetores de câmaras para serem utilizados nos veículos leves, médio, pesados... |
| 46854998000192 | HOSPITAL DO SERVIDOR PUBLICO MUNICIPAL | 46854998000192-1-000019/2026 | PMSP - HOSPITAL DO SERVIDOR PÚBLICO MUNICIPAL | Prestação de serviços contínuos de assistência técnica e manutenção integral - preventiva, corretiva, preditiva e eme... |
| 49269251000165 | SECRETARIA MUNICIPAL DE GESTAO - SG | 49269251000165-1-000001/2026 | PMSP - SEGES - COORD GESTÃO BENS E SERVIÇOS | Registro de preço para a prestação de Serviço Móvel Pessoal com dados, mensagens, acesso à internet banda larga móvel... |
| 74118514000182 | SAO PAULO SECRETARIA DO VERDE E DO MEIO AMBIENTE | 74118514000182-1-000001/2026 | PMSP - SECRETARIA DO VERDE E DO MEIO AMBIENTE | Aquisição de materiais de pintura para a manutenção das edificações que compõe os Parques Municipais de São Paulo. |
| 05245375000135 | SECRETARIA MUNICIPAL DE SEGURANCA URBANA - SMSU | 05245375000135-1-000004/2026 | PMSP - SECRETARIA MUNICIPAL SEGURANÇA URBANA | Constituição de Ata de Registro de Preços para a futura aquisição de pistolas calibre 9 mm NATO e Espingardas Calibre... |
| 05969123000159 | SUBPREFEITURA VILA PRUDENTE | 05969123000159-1-000001/2026 | PMSP - SUBPREFEITURA VILA PRUDENTE | CONTRATAÇÃO DE EMPRESA ESPECIALIZADA PARA A PRESTAÇÃO DE SERVIÇOS CONTINUADOS DE LOCAÇÃO E INSTALAÇÃO DE EQUIPAMENTOS... |
| 46392114000125 | SECRETARIA MUNICIPAL DE EDUCACAO | 46392114000125-1-000133/2026 | PMSP - SECRETARIA MUNICIPAL DE EDUCAÇÃO | Registro de Preços para aquisição de Luva descartável látex e nitrilo (tamanhos M e G) para as Unidades Escolares. |

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
| Rio de Janeiro | Valor homologado | 6 | 10 | 60.0% |
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
| Vitoria | Valor homologado | 3 | 10 | 30.0% |
| Vitoria | Data de publicacao | 10 | 10 | 100.0% |
| Vitoria | Abertura de proposta | 10 | 10 | 100.0% |
| Vitoria | Encerramento de proposta | 10 | 10 | 100.0% |
| Vitoria | Unidade | 10 | 10 | 100.0% |
| Vitoria | Link de origem | 0 | 10 | 0.0% |
| Vitoria | Documentos | 10 | 10 | 100.0% |

## Documentos vinculados

| Capital | Com docs | Amostra | Min docs | Max docs | Media docs | Tipos observados |
| --- | --- | --- | --- | --- | --- | --- |
| Sao Paulo | 10 | 10 | 1 | 1 | 1.0 | Edital |
| Rio de Janeiro | 10 | 10 | 1 | 1 | 1.0 | Edital |
| Belo Horizonte | 10 | 10 | 1 | 1 | 1.0 | Edital |
| Vitoria | 10 | 10 | 2 | 12 | 3.8 | Edital, Estudo Técnico Preliminar, Outros Documentos, Termo de Referência |

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
