---
name: pncp-sampling-methodologist
description: Use when changing the PNCP sampling method, Sao Paulo municipal CNPJ filter, exclusions, random seed, sample size, or study limitations.
---

# PNCP Sampling Methodologist

Use this skill before changing sample design.

## Rules

- Keep the target sample at 10 contracts per capital unless the research design changes.
- Use seed `20260608` for deterministic sampling.
- Sort by `numeroControlePNCP` before sampling.
- For Sao Paulo, use the municipality scan and filter municipal executive entities.
- Exclude legislative bodies such as Camara Municipal/CMSP from the main executive recut.
- If a city has fewer than 10 eligible records, include all and record the limitation.

## Sao Paulo Fragmentation

Treat multiple municipal CNPJs in Sao Paulo as an analytical finding, not merely a data-cleaning problem.
