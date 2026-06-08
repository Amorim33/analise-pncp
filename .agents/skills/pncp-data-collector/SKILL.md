---
name: pncp-data-collector
description: Use when collecting, refreshing, validating, or troubleshooting PNCP raw snapshots and processed data files in this analysis repository.
---

# PNCP Data Collector

Use this skill for data refreshes and reproducibility checks.

## Workflow

1. Run `uv run pncp-analysis collect` to refresh publication snapshots.
2. Confirm `data/raw/collection_metadata.json` records source counts and failures.
3. Run `uv run pncp-analysis sample` after any collection refresh.
4. Run `uv run pncp-analysis analyze` to fetch document metadata for sampled records.
5. Never silently accept non-JSON API responses; preserve failures in raw metadata.
6. Keep snapshots in `data/raw/` and derived tables in `data/processed/`.
7. Preserve enough raw data to show examples returned by the API in the report.
8. For Sao Paulo, keep both the matrix-CNPJ snapshot and the municipality-scan
   snapshot so the report can quantify records outside the matrix CNPJ.

## Smoke Test

Use this command for a small live API check:

```bash
uv run pncp-analysis collect --live --limit 1
```

## Fragmentation Evidence

After collection, verify `data/raw/collection_metadata.json` contains separate
sources for Sao Paulo matrix CNPJ and Sao Paulo municipality scan. If one source
is missing, do not update the final report until the gap is explained.
