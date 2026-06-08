Use the local skills in this order when maintaining the analysis:

1. `pncp-api-cartographer`: validate PNCP endpoints, parameters, and API behavior.
2. `pncp-data-collector`: collect or refresh API snapshots.
3. `pncp-sampling-methodologist`: review filters, sampling, exclusions, and limitations.
4. `pncp-report-writer`: generate or revise `analise-exploratoria.md`.

When revising the analysis, actively seek evidence for or against the Sao Paulo
fragmentation claim: compare matrix-CNPJ results with municipality-scan results,
list non-matrix municipal CNPJs, preserve concrete API examples, and check
whether similar fragmentation appears in the other capitals before making a
regional claim.

Before committing code changes, run `make check`.
