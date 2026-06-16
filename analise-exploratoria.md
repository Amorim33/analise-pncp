# Analise exploratoria do PNCP nas capitais do Sudeste

## Resumo

Esta analise compara contratacoes de Pregao Eletronico publicadas no PNCP entre 15/06/2025 a 15/06/2026 pelas capitais do Sudeste. O desenho e exploratorio: ele busca avaliar transparencia, completude dos dados e fragmentacao institucional, sem pretender representar todos os municipios da regiao.

O metodo combina coleta por **API**^[**API**: interface de programacao de aplicacoes; neste trabalho, e o meio automatizado de consulta aos dados do PNCP.], analise de completude e medicao de consumibilidade dos endpoints. O processo foi apoiado pelo **Codex**^[**Codex**: agente de programacao e documentacao usado para implementar, validar e revisar o pipeline.] e organizado por **skills**^[**Skills**: instrucoes locais que especializam agentes para tarefas como mapear a **API**, coletar dados, revisar amostragem e redigir o relatorio.].

O principal achado metodologico e que Sao Paulo aparece de forma fragmentada: a consulta apenas pelo CNPJ matriz subrepresenta o municipio, enquanto a busca por codigo IBGE revela varios CNPJs municipais executivos.

## Questoes de pesquisa

- Q1. Ha completude nos dados fornecidos pelo PNCP nas prefeituras das capitais dos estados do Sudeste brasileiro (Sao Paulo, Rio de Janeiro, Belo Horizonte e Vitoria)?
- Q2. Os dados das **APIs** do PNCP sao facilmente consumiveis?
- Q3. As respostas da **API** do PNCP sao semanticamente coerentes e informativas para controle social?

## Metodologia

| Parametro | Valor |
| --- | --- |
| Periodo | 15/06/2025 a 15/06/2026 |
| Modalidade | Pregao - Eletronico (6) |
| Amostra principal | todos os registros elegiveis no periodo |
| Amostra documental | ate 100 por capital (400 registros no total) |
| Amostra Q3 | documento principal da subamostra documental |
| Modelo Q3 | codex-subagent |
| Seed | 20260608 |

Para Rio de Janeiro, Belo Horizonte e Vitoria, a coleta usou o CNPJ matriz do municipio. Para Sao Paulo, a coleta combinou o CNPJ matriz com uma busca por UF e codigo IBGE, filtrando orgaos municipais executivos e excluindo orgaos legislativos como a Camara Municipal.

## Reprodutibilidade e processo agentico

O repositorio GitHub <https://github.com/Amorim33/analise-pncp> versiona o codigo Python, configuracoes, snapshots brutos, tabelas processadas, metricas, analise exploratoria e relatorio final. O processo foi assistido pelo **Codex** como agente de programacao e documentacao, sob supervisao humana.

A divisao agentica foi registrada em **skills** locais no caminho `.agents/skills/`, com papeis para mapeamento da **API**, coleta de dados, metodologia de amostragem, avaliacao semantica e redacao do relatorio. As decisoes substantivas, validacao de fontes e interpretacao final permanecem sob responsabilidade do autor.

## Exemplos de registros retornados pela API

Os exemplos abaixo usam um subconjunto dos campos retornados pela API do PNCP. Eles mostram como a informacao chega para a analise: identificador PNCP, orgao, unidade, objeto, valores, situacao, link de origem e documentos vinculados.

### Sao Paulo - exemplo fora do CNPJ matriz

```json
{
  "documentos": [],
  "linkSistemaOrigem": "",
  "numeroControlePNCP": "01164292000160-1-000020/2026",
  "objetoCompra": "CONTRATAÇÃO DE EMPRESA DO RAMO PARA A AQUISIÇÃO E INSTALAÇÃO DE PARQUE INFANTIL, DEVIDAMENTE CERTIFICADO POR ÓRGÃO COMPETENTE, PARA ATENDER AS NECESSIDADES DO FUNDO MUNICIPAL DE EDUCAÇÃO/FME, CONFORME EMENDA PARLAMENTAR Nº 1299.2/2025, PROCESSO Nº 202500005022377.",
  "orgaoEntidade": {
    "cnpj": "01164292000160",
    "esferaId": "M",
    "poderId": "N",
    "razaoSocial": "MUNICIPIO DE CACU"
  },
  "situacaoCompraNome": "Divulgada no PNCP",
  "unidadeOrgao": {
    "codigoIbge": "3550308",
    "codigoUnidade": "0",
    "municipioNome": "São Paulo",
    "nomeUnidade": "PREFEITURA MUNICIPAL DE CAÇU",
    "ufNome": "São Paulo",
    "ufSigla": "SP"
  },
  "valorTotalEstimado": 137600.4,
  "valorTotalHomologado": null
}
```
### Sao Paulo - exemplo no CNPJ matriz

```json
{
  "documentos": [],
  "linkSistemaOrigem": "https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/landing?destino=acompanhamento-compra&compra=92505605900042026",
  "numeroControlePNCP": "46395000000139-1-000007/2026",
  "objetoCompra": "Aquisição de materiais de construção, abrangendo itens das linhas hidráulica, elétrica, ferragens, pintura, alvenaria, acabamentos e correlatos, conforme as especificações, quantidades e condições estabelecidas neste Termo de Referência considerando AUSÊNCIA de código específico para cada item no www.gov.br/compras, solicitamos que para a formação da proposta de preços e o registro no sistema, o licitante baseie-se EXCLUSIVAMENTE, nas informações nas ESPECIFICAÇÕES.  ",
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
  "valorTotalEstimado": 62640.7,
  "valorTotalHomologado": 42066.57
}
```
### Rio de Janeiro

```json
{
  "documentos": [],
  "linkSistemaOrigem": "https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/landing?destino=acompanhamento-compra&compra=98600105900012026",
  "numeroControlePNCP": "42498733000148-1-000104/2026",
  "objetoCompra": "CoNTRATAÇÃO DE EMPRESA ESPECIALIZADA PARA PRESTAÇÃO DE SERVIÇOS DE PLANEJAMENTO, ORGANIZAÇÃO, EXECUÇÃO, ACOMPANHAMENTO, FORNECIMENTO DE BENS E INSUMOS, INFRAESTRUTURA E APOIO LOGÍSTICO, VISANDO A REALIZAÇÃO DO BAILE DA CINELÂNDIA E DESFILES DA AVENIDA CHILE, CARNAVAL DO RIO 2026",
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
  "valorTotalEstimado": 0.0,
  "valorTotalHomologado": null
}
```
### Belo Horizonte

```json
{
  "documentos": [],
  "linkSistemaOrigem": "https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/landing?destino=acompanhamento-compra&compra=98412305970012026",
  "numeroControlePNCP": "18715383000140-1-000024/2026",
  "objetoCompra": "O objeto da presente licitação é a aquisição de COLETES DE PROTEÇÃO BALÍSTICA FLEXÍVEL, PARA USO POLICIAL, NÍVEL DE PROTEÇÃO III-A, COM CAPA EXTERNA TIPO MODULAR (COM CAPA SOBRESSALENTE TIPO MODULAR), com a finalidade de atender atividades operacionais da Guarda Civil Municipal de Belo Horizonte, conforme condições e exigências estabelecidas neste Edital, Termo de Referência e demais anexos.",
  "orgaoEntidade": {
    "cnpj": "18715383000140",
    "esferaId": "M",
    "poderId": "N",
    "razaoSocial": "MUNICIPIO DE BELO HORIZONTE"
  },
  "situacaoCompraNome": "Divulgada no PNCP",
  "unidadeOrgao": {
    "codigoIbge": "3106200",
    "codigoUnidade": "984123",
    "municipioNome": "Belo Horizonte",
    "nomeUnidade": "PREF.MUN.DE BELO HORIZONTE",
    "ufNome": "Minas Gerais",
    "ufSigla": "MG"
  },
  "valorTotalEstimado": 3585413.35,
  "valorTotalHomologado": 1969468.81
}
```
### Vitoria

```json
{
  "documentos": [],
  "linkSistemaOrigem": null,
  "numeroControlePNCP": "27142058000126-1-000005/2026",
  "objetoCompra": "AQUISIÇÃO DE CLIMATIZADORES DE AR",
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
  "valorTotalEstimado": 31435.32,
  "valorTotalHomologado": 28209.6
}
```

## Amostra

| Capital | Registros candidatos | Amostra | CNPJs distintos | Registros no CNPJ matriz | Participacao da matriz |
| --- | --- | --- | --- | --- | --- |
| Sao Paulo | 2662 | 2662 | 67 | 30 | 1.1% |
| Rio de Janeiro | 896 | 896 | 1 | 896 | 100.0% |
| Belo Horizonte | 291 | 291 | 1 | 291 | 100.0% |
| Vitoria | 234 | 234 | 1 | 234 | 100.0% |

A amostra principal inclui todos os registros elegiveis no periodo, apos deduplicacao por `numeroControlePNCP`. Para documentos vinculados, o pipeline usa uma subamostra deterministica de ate 100 registros por capital, tambem ordenada e sorteada com seed reprodutivel.

## Resultados

| Capital | Controle PNCP | CNPJ | Orgao | Docs |
| --- | --- | --- | --- | --- |
| Sao Paulo | 01164292000160-1-000020/2026 | 01164292000160 | MUNICIPIO DE CACU | 0 |
| Sao Paulo | 01164292000160-1-000033/2026 | 01164292000160 | MUNICIPIO DE CACU | 0 |
| Sao Paulo | 01164292000160-1-000037/2026 | 01164292000160 | MUNICIPIO DE CACU | 0 |
| Sao Paulo | 01164292000160-1-000039/2025 | 01164292000160 | MUNICIPIO DE CACU | 0 |
| Sao Paulo | 04537740000112-1-000002/2026 | 04537740000112 | SECRETARIA MUNICIPAL DE DESENVOLVIMENTO ECONOMICO E TRABALHO | 0 |
| Sao Paulo | 04537740000112-1-000010/2025 | 04537740000112 | SECRETARIA MUNICIPAL DE DESENVOLVIMENTO ECONOMICO E TRABALHO | 0 |
| Sao Paulo | 04537740000112-1-000012/2025 | 04537740000112 | SECRETARIA MUNICIPAL DE DESENVOLVIMENTO ECONOMICO E TRABALHO | 0 |
| Sao Paulo | 04537740000112-1-000013/2025 | 04537740000112 | SECRETARIA MUNICIPAL DE DESENVOLVIMENTO ECONOMICO E TRABALHO | 0 |
| Sao Paulo | 04545693000159-1-000003/2025 | 04545693000159 | SECRETARIA MUNICIPAL DE JUSTICA | 0 |
| Sao Paulo | 05245375000135-1-000004/2026 | 05245375000135 | SECRETARIA MUNICIPAL DE SEGURANCA URBANA - SMSU | 0 |
| Sao Paulo | 05245375000135-1-000005/2026 | 05245375000135 | SECRETARIA MUNICIPAL DE SEGURANCA URBANA - SMSU | 0 |
| Sao Paulo | 05245375000135-1-000007/2026 | 05245375000135 | SECRETARIA MUNICIPAL DE SEGURANCA URBANA - SMSU | 0 |
| Sao Paulo | 05245375000135-1-000009/2026 | 05245375000135 | SECRETARIA MUNICIPAL DE SEGURANCA URBANA - SMSU | 0 |
| Sao Paulo | 05245375000135-1-000012/2026 | 05245375000135 | SECRETARIA MUNICIPAL DE SEGURANCA URBANA - SMSU | 0 |
| Sao Paulo | 05245375000135-1-000014/2026 | 05245375000135 | SECRETARIA MUNICIPAL DE SEGURANCA URBANA - SMSU | 0 |
| Sao Paulo | 05245375000135-1-000015/2026 | 05245375000135 | SECRETARIA MUNICIPAL DE SEGURANCA URBANA - SMSU | 0 |
| Sao Paulo | 05245375000135-1-000016/2025 | 05245375000135 | SECRETARIA MUNICIPAL DE SEGURANCA URBANA - SMSU | 0 |
| Sao Paulo | 05245375000135-1-000016/2026 | 05245375000135 | SECRETARIA MUNICIPAL DE SEGURANCA URBANA - SMSU | 0 |
| Sao Paulo | 05245375000135-1-000017/2025 | 05245375000135 | SECRETARIA MUNICIPAL DE SEGURANCA URBANA - SMSU | 0 |
| Sao Paulo | 05245375000135-1-000018/2025 | 05245375000135 | SECRETARIA MUNICIPAL DE SEGURANCA URBANA - SMSU | 0 |
| Sao Paulo | 05245375000135-1-000018/2026 | 05245375000135 | SECRETARIA MUNICIPAL DE SEGURANCA URBANA - SMSU | 0 |
| Sao Paulo | 05245375000135-1-000020/2025 | 05245375000135 | SECRETARIA MUNICIPAL DE SEGURANCA URBANA - SMSU | 0 |
| Sao Paulo | 05245375000135-1-000025/2025 | 05245375000135 | SECRETARIA MUNICIPAL DE SEGURANCA URBANA - SMSU | 0 |
| Sao Paulo | 05245375000135-1-000026/2025 | 05245375000135 | SECRETARIA MUNICIPAL DE SEGURANCA URBANA - SMSU | 1 |
| Sao Paulo | 05245375000135-1-000027/2025 | 05245375000135 | SECRETARIA MUNICIPAL DE SEGURANCA URBANA - SMSU | 0 |

_Tabela limitada aos primeiros 25 registros de 4083 elegiveis para manter o relatorio legivel._

## Constatações adicionais

- Na amostra candidata de Sao Paulo, 98.9% dos registros elegiveis ficaram fora do CNPJ matriz; nas demais capitais analisadas, os registros por CNPJ matriz concentraram 100% dos candidatos coletados.
- Sao Paulo apresentou 67 CNPJs distintos no recorte elegivel, enquanto Rio de Janeiro, Belo Horizonte e Vitoria apareceram com um CNPJ cada no recorte por matriz.
- Vitoria teve documentos vinculados em todos os itens da subamostra documental, mas nenhum dos registros elegiveis trouxe `linkSistemaOrigem`, o que reduz a rastreabilidade para o sistema de origem.
- O valor homologado apareceu com menor completude em Sao Paulo (60.4%), indicando que parte dos registros estava em fase anterior ao resultado ou sem homologacao registrada no recorte.
- A quantidade de documentos anexados variou de forma relevante: em Vitoria, um item da amostra chegou a 12 documentos, enquanto outros municipios tiveram padrao mais concentrado.

## Fragmentacao de CNPJs em Sao Paulo

| Metrica | Valor |
| --- | --- |
| CNPJ matriz | 46395000000139 |
| Registros candidatos de Sao Paulo | 2662 |
| Registros no CNPJ matriz | 30 |
| Registros fora do CNPJ matriz | 2632 |
| Participacao fora do CNPJ matriz | 98.9% |
| CNPJs distintos no recorte | 67 |
| CNPJs distintos fora da matriz | 66 |

A tabela abaixo mostra os principais CNPJs municipais encontrados no recorte de Sao Paulo apos o filtro de orgaos executivos municipais.

| CNPJ | Razao social | Registros |
| --- | --- | --- |
| 13864377000130 | FUNDO MUNICIPAL DE SAUDE - FMS | 1426 |
| 46854998000192 | HOSPITAL DO SERVIDOR PUBLICO MUNICIPAL | 400 |
| 46392114000125 | SECRETARIA MUNICIPAL DE EDUCACAO | 94 |
| 05667941000105 | SUBPREFEITURA DE GUAIANASES | 53 |
| 05499294000161 | SUBPREFEITURA SE | 34 |
| 49269244000163 | SAO PAULO SECRETARIA MUNICIPAL DE CULTURA | 33 |
| 05245375000135 | SECRETARIA MUNICIPAL DE SEGURANCA URBANA - SMSU | 31 |
| 46395000000139 | MUNICIPIO DE SAO PAULO | 30 |
| 05604369000127 | SUBPREFEITURA CAMPO LIMPO | 27 |
| 60269453000140 | SECRETARIA MUNICIPAL DE ASSISTENCIA E DESENVOLVIMENTO SOCIAL | 25 |

Exemplos de registros fora do CNPJ matriz reforcam que a fragmentacao nao e apenas nominal: diferentes CNPJs publicam objetos e unidades administrativas proprias no PNCP.

| CNPJ | Orgao | Controle PNCP | Unidade | Objeto |
| --- | --- | --- | --- | --- |
| 13864377000130 | FUNDO MUNICIPAL DE SAUDE - FMS | 13864377000130-1-000005/2026 | PMSP - SECRETARIA MUNICIPAL DE SAÚDE | Registro de Preços para o Fornecimento de LENCOL DE PAPEL DESCARTAVEL —70 CM X 50 M |
| 46854998000192 | HOSPITAL DO SERVIDOR PUBLICO MUNICIPAL | 46854998000192-1-000001/2026 | PMSP - HOSPITAL DO SERVIDOR PÚBLICO MUNICIPAL | Registro De Preços Para O Fornecimento De Material Médico Hospitalar (Fio Cirúrgico Multifilamentar Trançado De Polig... |
| 46392114000125 | SECRETARIA MUNICIPAL DE EDUCACAO | 46392114000125-1-000133/2026 | PMSP - SECRETARIA MUNICIPAL DE EDUCAÇÃO | Registro de Preços para aquisição de Luva descartável látex e nitrilo (tamanhos M e G) para as Unidades Escolares. |
| 05667941000105 | SUBPREFEITURA DE GUAIANASES | 05667941000105-1-000001/2026 | PMSP - SUBPREFEITURA GUAIANASES | Prestação de Serviços de Recuperação de Superfícies Pichadas. |
| 05499294000161 | SUBPREFEITURA SE | 05499294000161-1-000001/2026 | PMSP - SUBPREFEITURA SÉ | Contratação de empresa para a execução de serviços de requalificação da Praça Rotary, localizada entre a Rua General ... |
| 49269244000163 | SAO PAULO SECRETARIA MUNICIPAL DE CULTURA | 49269244000163-1-000012/2026 | PMSP - SECRETARIA MUNICIPAL DE CULTURA/SP | O presente pregão tem por objeto a prestação de serviços de apoio de segurança contra incêndio, pânico, abandono de e... |
| 05245375000135 | SECRETARIA MUNICIPAL DE SEGURANCA URBANA - SMSU | 05245375000135-1-000004/2026 | PMSP - SECRETARIA MUNICIPAL SEGURANÇA URBANA | Constituição de Ata de Registro de Preços para a futura aquisição de pistolas calibre 9 mm NATO e Espingardas Calibre... |
| 05604369000127 | SUBPREFEITURA CAMPO LIMPO | 05604369000127-1-000005/2026 | PMSP - SUBPREFEITURA CAMPO LIMPO | Contratação DE SERVIÇOS TÉCNICOS ESPECIALIZADOS PARA A EXECUÇÃO DE OBRAS DE REQUALIFICAÇÃO DE VIELA E CONSTRUÇÃO DE Q... |

Esse resultado sugere que a transparencia via PNCP nao depende apenas da existencia do portal, mas tambem da forma como a administracao estrutura e publica seus registros. Uma busca pelo CNPJ matriz de Sao Paulo tende a perder contratacoes relevantes de secretarias, fundos, empresas e unidades municipais.

## Completude dos dados

Para Q1, a completude foi avaliada campo a campo na amostra principal, que contem todos os registros elegiveis. Objeto, valor estimado, datas basicas e unidade administrativa aparecem como campos de alta disponibilidade; as maiores fragilidades estao em valor homologado, link do sistema de origem e, no caso de documentos, na subamostra documental.

| Capital | Objeto | Valor estimado | Valor homologado | Data de publicacao | Unidade | Link de origem | Documentos |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Sao Paulo | 100.0% | 100.0% | 60.4% | 100.0% | 100.0% | 99.8% | 100.0% |
| Rio de Janeiro | 100.0% | 100.0% | 62.8% | 100.0% | 100.0% | 100.0% | 100.0% |
| Belo Horizonte | 100.0% | 100.0% | 78.0% | 100.0% | 100.0% | 96.9% | 100.0% |
| Vitoria | 100.0% | 100.0% | 66.7% | 100.0% | 100.0% | 0.0% | 100.0% |

Exemplos sorteados de forma pseudoaleatoria, com seed fixa:

| Capital | Controle PNCP | Data | Valor homologado | Link | Docs | Objeto |
| --- | --- | --- | --- | --- | --- | --- |
| Sao Paulo | 13864377000130-1-002050/2025 | 18/11/2025 | presente | presente | 1 | REGISTRO De PREÇOS PARA O FORNECIMENTO CANULA TRAQUEOSTOMIA COM BALAO, DESCARTAVEL, EST... |
| Rio de Janeiro | 42498733000148-1-001315/2025 | 24/07/2025 | presente | presente | 1 | Aquisição de Equipamento de Proteção Individual –EPI |
| Belo Horizonte | 18715383000140-1-000189/2026 | 27/03/2026 | presente | presente | 1 | O objeto da presente licitação é o registro de preços para aquisição de materiais de hi... |
| Vitoria | 27142058000126-1-000676/2025 | 28/11/2025 | presente | ausente | 6 | REGISTRO DE PREÇOS VISANDO FUTURO E EVENTUAL FORNECIMENTO DE ÁGUA MINERAL GALÃO 20L |

Tabela completa de campos analisados:

| Capital | Campo | Presentes | Amostra | Percentual |
| --- | --- | --- | --- | --- |
| Sao Paulo | Objeto | 2662 | 2662 | 100.0% |
| Sao Paulo | Valor estimado | 2662 | 2662 | 100.0% |
| Sao Paulo | Valor homologado | 1608 | 2662 | 60.4% |
| Sao Paulo | Data de publicacao | 2662 | 2662 | 100.0% |
| Sao Paulo | Abertura de proposta | 2662 | 2662 | 100.0% |
| Sao Paulo | Encerramento de proposta | 2662 | 2662 | 100.0% |
| Sao Paulo | Unidade | 2662 | 2662 | 100.0% |
| Sao Paulo | Link de origem | 2658 | 2662 | 99.8% |
| Sao Paulo | Documentos | 100 | 100 | 100.0% |
| Rio de Janeiro | Objeto | 896 | 896 | 100.0% |
| Rio de Janeiro | Valor estimado | 896 | 896 | 100.0% |
| Rio de Janeiro | Valor homologado | 563 | 896 | 62.8% |
| Rio de Janeiro | Data de publicacao | 896 | 896 | 100.0% |
| Rio de Janeiro | Abertura de proposta | 896 | 896 | 100.0% |
| Rio de Janeiro | Encerramento de proposta | 896 | 896 | 100.0% |
| Rio de Janeiro | Unidade | 896 | 896 | 100.0% |
| Rio de Janeiro | Link de origem | 896 | 896 | 100.0% |
| Rio de Janeiro | Documentos | 100 | 100 | 100.0% |
| Belo Horizonte | Objeto | 291 | 291 | 100.0% |
| Belo Horizonte | Valor estimado | 291 | 291 | 100.0% |
| Belo Horizonte | Valor homologado | 227 | 291 | 78.0% |
| Belo Horizonte | Data de publicacao | 291 | 291 | 100.0% |
| Belo Horizonte | Abertura de proposta | 291 | 291 | 100.0% |
| Belo Horizonte | Encerramento de proposta | 291 | 291 | 100.0% |
| Belo Horizonte | Unidade | 291 | 291 | 100.0% |
| Belo Horizonte | Link de origem | 282 | 291 | 96.9% |
| Belo Horizonte | Documentos | 100 | 100 | 100.0% |
| Vitoria | Objeto | 234 | 234 | 100.0% |
| Vitoria | Valor estimado | 234 | 234 | 100.0% |
| Vitoria | Valor homologado | 156 | 234 | 66.7% |
| Vitoria | Data de publicacao | 234 | 234 | 100.0% |
| Vitoria | Abertura de proposta | 234 | 234 | 100.0% |
| Vitoria | Encerramento de proposta | 234 | 234 | 100.0% |
| Vitoria | Unidade | 234 | 234 | 100.0% |
| Vitoria | Link de origem | 0 | 234 | 0.0% |
| Vitoria | Documentos | 100 | 100 | 100.0% |

## Documentos vinculados

| Capital | Com docs | Amostra | Min docs | Max docs | Media docs | Tipos observados |
| --- | --- | --- | --- | --- | --- | --- |
| Sao Paulo | 100 | 100 | 1 | 1 | 1.0 | Edital |
| Rio de Janeiro | 100 | 100 | 1 | 1 | 1.0 | Edital |
| Belo Horizonte | 100 | 100 | 1 | 2 | 1.0 | Edital, Outros Documentos, Termo de Referência |
| Vitoria | 100 | 100 | 1 | 12 | 5.3 | DFD, Edital, Estudo Técnico Preliminar, Mapa de Riscos, Outros Documentos |

A presenca de objeto, datas, valores, unidade administrativa e link de origem foi medida no universo elegivel. Documentos vinculados foram medidos na subamostra documental. Essas metricas nao avaliam a qualidade textual dos documentos, mas indicam se um cidadao ou pesquisador consegue localizar informacoes basicas para controle social.

## Consumo da API

Para Q2, o pipeline registrou a duracao da coleta e das chamadas ao endpoint de documentos, alem do tempo medio de resposta bem-sucedida. A facilidade de consumo e parcial: a API e estruturada e paginada, mas exige controle de janela temporal, backoff para limite de taxa e validacao de `Content-Type` para evitar parse de respostas nao JSON.

| Etapa | Requisições | Sucessos | Tempo médio | Duração | Falhas |
| --- | --- | --- | --- | --- | --- |
| Snapshots de contratações | n/a | n/a | n/a | n/a | n/a |
| Tentativa live de coleta | 6 | 0 | n/a | 2min 56.6s | 6 |
| Consulta de documentos | 400 | 400 | 0.10s | 40.51s | 0 |
| Experimento total do relatório |  |  |  | 3min 37.8s |  |

- Historico local desta sessao: em 16/06/2026, a tentativa live de coleta em `/v1/contratacoes/publicacao` durou 2min 56.6s, realizou 6 requisicoes, obteve 0 respostas bem-sucedidas e acumulou 6 falhas. O registro combina 2 timeouts e 4 respostas HTTP 503 (Service Unavailable). Dessas respostas, 4 vieram com corpo HTML (`text/html`), nao como JSON. Como havia snapshots anteriores, o pipeline acionou fallback, reutilizou os dados brutos existentes e concluiu o fluxo do relatorio em 3min 37.8s.
- Consulta documental: 400/400 chamadas foram bem-sucedidas, com tempo medio de 0.10s, maximo de 0.44s e 0 falhas persistentes. A API e consumivel, mas a execucao mostrou dependencia de retries, backoff, validacao de `Content-Type`, quebra temporal da coleta e snapshots auditaveis.

- Os snapshots de coleta reutilizados registravam 0 falhas persistentes na coleta bem-sucedida anterior.
- Na execução final, a consulta de documentos registrou 0 falhas persistentes.
- A tentativa live desta execução falhou e o pipeline reutilizou snapshots existentes. O erro bruto completo permanece preservado em `data/raw/collection_attempt_metadata.json` e `data/processed/pipeline_metadata.json`; a sintese operacional e a resposta HTTP 503 em HTML e os timeouts descritos acima.
- Durante a experimentação: HTTP 429 em chamadas repetidas, tratado com backoff e nova tentativa.
- Durante a experimentação: Timeouts em paginação anual longa, mitigados pela coleta em chunks mensais de 31 dias.
- Durante a experimentação: Risco de resposta HTML com HTTP 200, tratado por validação de Content-Type antes do parse JSON.

## Qualidade semantica e informatividade

Para Q3, o pipeline seleciona um documento principal por contratacao da subamostra documental e usa um subagent Codex como avaliador estruturado. Quando o texto documental nao esta extraido, a avaliacao fica limitada ao registro da **API** e aos metadados do documento principal. O avaliador nao e fonte de verdade: a evidencia auditavel fica nos snapshots, metadados, hashes dos inputs e respostas preservadas.

A Q3 usou o prompt `q3-semantic-v1` e o schema `q3-semantic-schema-v1`. O avaliador registrado foi `codex-subagent`. Foram pontuados 400 de 400 registros da subamostra; 397 ficaram com texto documental insuficiente.

| Capital | Pontuados | Texto insuf. | Amostra | Coer. | Info. | Doc/API | Acion. | Media |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Belo Horizonte | 100 | 100 | 100 | 3.96 | 3.53 | 1.00 | 1.80 | 2.57 |
| Rio de Janeiro | 100 | 98 | 100 | 3.97 | 3.71 | 1.06 | 2.00 | 2.69 |
| Sao Paulo | 100 | 99 | 100 | 3.98 | 3.36 | 1.03 | 1.91 | 2.57 |
| Vitoria | 100 | 100 | 100 | 3.95 | 2.60 | 1.00 | 0.65 | 2.05 |

Exemplos de avaliacao:

- Vitoria (`27142058000126-1-000008/2026`), media 1.25: Avaliacao local Codex: status=insufficient_text; media=1.25; alinhamento lexical documento/API=0.000. Alertas: Objeto da compra e curto ou generico.; Objeto nao delimita suficientemente escopo, finalidade ou item contratado.; Link do sistema de origem ausente.; Texto ...
- Vitoria (`27142058000126-1-000270/2026`), media 1.25: Avaliacao local Codex: status=insufficient_text; media=1.25; alinhamento lexical documento/API=0.000. Alertas: Objeto da compra e curto ou generico.; Objeto nao delimita suficientemente escopo, finalidade ou item contratado.; Link do sistema de origem ausente.; Texto ...
- Vitoria (`27142058000126-1-000319/2025`), media 1.25: Avaliacao local Codex: status=insufficient_text; media=1.25; alinhamento lexical documento/API=0.000. Alertas: Objeto da compra e curto ou generico.; Objeto nao delimita suficientemente escopo, finalidade ou item contratado.; Link do sistema de origem ausente.; Texto ...
- Vitoria (`27142058000126-1-000634/2025`), media 1.25: Avaliacao local Codex: status=insufficient_text; media=1.25; alinhamento lexical documento/API=0.000. Alertas: Objeto da compra e curto ou generico.; Objeto nao delimita suficientemente escopo, finalidade ou item contratado.; Link do sistema de origem ausente.; Texto ...
- Vitoria (`27142058000126-1-000783/2025`), media 1.25: Avaliacao local Codex: status=insufficient_text; media=1.25; alinhamento lexical documento/API=0.000. Alertas: Objeto da compra e curto ou generico.; Objeto nao delimita suficientemente escopo, finalidade ou item contratado.; Link do sistema de origem ausente.; Texto ...
- Rio de Janeiro (`42498733000148-1-000665/2026`), media 1.50: Avaliacao local Codex: status=insufficient_text; media=1.50; alinhamento lexical documento/API=0.000. Alertas: Objeto da compra e curto ou generico.; Objeto nao delimita suficientemente escopo, finalidade ou item contratado.; Valor estimado zero sem valor homologado i...

Limitacoes especificas da Q3:

- Avaliacao executada localmente pelo Codex como regra deterministica derivada da rubrica, sem chamada a API externa de modelo e sem conhecimento externo.
- O alinhamento documento/API usa sobreposicao lexical entre objeto, modalidade, orgao e texto extraido; baixa sobreposicao indica risco de verificabilidade, nao prova contradicao substantiva.
- Caracteres substitutos invalidos em extracoes documentais foram saneados para UTF-8 antes de hashing e gravacao; text_sha256 refere-se ao texto saneado.
- 397 documento(s) da subamostra nao tiveram texto extraido com status ok.
- 397 registro(s) receberam status insufficient_text por ausencia ou insuficiencia de texto documental.

## Limitacoes

- A comparacao e exploratoria e nao representa todos os municipios do Sudeste.
- Sao Paulo possui registros municipais distribuidos em varios CNPJs, o que exige filtro por municipio e orgao.
- A API de consulta por publicacao limita cada requisicao a janelas de ate 365 dias; por isso o recorte usa a maior janela aceita em uma consulta reprodutivel.
- A varredura municipal de Sao Paulo coleta todas as paginas retornadas pela API para a janela anual.
- A API pode retornar payload HTML de bloqueio com HTTP 200; o coletor valida Content-Type e registra falhas.

## Conclusao regional

O PNCP oferece uma infraestrutura relevante de governo aberto para as capitais do Sudeste, pois centraliza registros, padroniza campos e permite consulta por API. No entanto, a comparacao mostra que a abertura formal dos dados nao elimina assimetrias de acesso. A fragmentacao de CNPJs em Sao Paulo e um achado substantivo: mesmo com dados publicos, a capacidade de controle social depende de conhecer a organizacao administrativa por tras dos registros.

Assim, a conclusao regional e que o PNCP fortalece a transparencia formal, mas sua efetividade como instrumento de governo aberto depende da completude documental, da padronizacao dos registros, da qualidade semantica das informacoes retornadas e da facilidade de reconstituir o universo institucional de cada prefeitura.

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
