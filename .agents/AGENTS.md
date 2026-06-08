Use the local skills in this order when maintaining the analysis:

1. `pncp-api-cartographer`: validate PNCP endpoints, parameters, and API behavior.
2. `pncp-data-collector`: collect or refresh API snapshots.
3. `pncp-sampling-methodologist`: review filters, sampling, exclusions, and limitations.
4. `pncp-report-writer`: generate or revise `analise-exploratoria.md`.

Before committing code changes, run `make check`.
