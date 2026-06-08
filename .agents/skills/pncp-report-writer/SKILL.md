---
name: pncp-report-writer
description: Use when generating, revising, or reviewing analise-exploratoria.md from PNCP metrics, samples, and methodological notes.
---

# PNCP Report Writer

Use this skill for the final Markdown artifact.

## Required Sections

- Resumo executivo
- Metodologia
- Exemplos de registros retornados pela API
- Amostra
- Resultados
- Constatações adicionais
- Fragmentacao de CNPJs em Sao Paulo
- Completude dos dados
- Documentos vinculados
- Limitacoes
- Conclusao regional
- Reproducibilidade
- Referencias tecnicas

## Style

Write in Portuguese academic prose. Be explicit that the result is exploratory, not a statistical representation of all municipalities in the Sudeste. Highlight the Sao Paulo CNPJ fragmentation as a substantive finding for government openness and control social.

## Evidence Standard

Do not state that Sao Paulo is more fragmented without showing:

- matrix-CNPJ count and share;
- non-matrix count and share;
- distinct CNPJ count;
- examples of returned API records outside the matrix CNPJ;
- a contrast with the other capitals in the same recut.

Include concrete API examples, but show compact JSON subsets rather than full raw
payloads.
