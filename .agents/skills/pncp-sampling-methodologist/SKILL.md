---
name: pncp-sampling-methodologist
description: Use when changing the PNCP sampling method, Sao Paulo municipal CNPJ filter, exclusions, random seed, sample size, or study limitations.
---

# PNCP Sampling Methodologist

Use this skill before changing sample design.

## Rules

- Use all eligible records as the main analytical sample when `sample.strategy`
  is `all`.
- Use `sample.document_n` as the deterministic document sub-sample limit per
  capital.
- Use seed `20260608` for deterministic sampling.
- Sort by `numeroControlePNCP` before sampling.
- For Sao Paulo, use the municipality scan and filter municipal executive entities.
- Exclude legislative bodies such as Camara Municipal/CMSP from the main executive recut.
- If a city has fewer records than the document sub-sample limit, include all
  available records for document lookup and record the limitation.
- Combine Sao Paulo matrix-CNPJ records with filtered municipality-scan records
  before deduplication.
- Report the share and count of Sao Paulo records outside the CNPJ matrix.
- Compare Sao Paulo's distinct CNPJ count against the other capitals before
  framing fragmentation as a regional contrast.

## Sao Paulo Fragmentation

Treat multiple municipal CNPJs in Sao Paulo as an analytical finding, not merely a data-cleaning problem.

Look for concrete evidence:

- non-matrix CNPJ count;
- top non-matrix CNPJs and their orgao/unidade names;
- example `numeroControlePNCP` values outside the matrix;
- whether non-matrix records have distinct objects, document links, or units.
