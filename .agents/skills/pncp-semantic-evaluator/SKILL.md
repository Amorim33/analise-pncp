---
name: pncp-semantic-evaluator
description: Use when evaluating PNCP response semantic quality, document/API alignment, Codex subagent evaluation artifacts, Q3 metrics, or semantic/informational quality in this analysis repository.
---

# PNCP Semantic Evaluator

Use this skill for Q3: semantic coherence and informativeness of PNCP API
responses for social control.

## Workflow

1. Use `data/processed/document_sample.json` as the Q3 population.
2. Select exactly one principal document per contract unless the user explicitly
   changes the design.
3. Prefer active `Edital` documents; prefer revised, republished, consolidated,
   or updated titles; then use the highest `sequencialDocumento`.
4. Preserve hashes for downloaded bytes, extracted text, evaluator inputs, and
   raw evaluator responses.
5. Extract text from PDF, DOCX, TXT/HTML, and supported files inside ZIP archives.
6. Use a Codex subagent as an evaluator, not as a source of truth. The evidence
   is the API snapshot, selected document metadata, extracted text, hashes, and
   saved output.
7. Use the Q3 schema and keep prompt/schema versions in
   every row.
8. Report extraction failures and evaluator variance as limitations.

## Rubric

Use integer scores from 0 to 4:

- `coerencia_interna`: city, UF, IBGE, CNPJ, orgao, unidade, object, dates,
  and values are mutually consistent.
- `informatividade_do_registro`: the API record explains what is contracted, by
  whom, for what purpose, and at what scope.
- `alinhamento_documento_api`: the principal document confirms or contradicts
  object, orgao, modality, dates, and values from the API.
- `acionabilidade_controle_social`: a citizen can use the returned information
  to continue oversight or verification.

## Commands

```bash
uv run pncp-analysis semantic
uv run pncp-analysis semantic --reuse-existing
uv run pncp-analysis semantic --skip-gpt
```

Run `make check` before committing.
