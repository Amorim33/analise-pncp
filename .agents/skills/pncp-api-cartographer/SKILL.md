---
name: pncp-api-cartographer
description: Use when validating PNCP API endpoints, parameters, response schemas, modality codes, base URL fallbacks, or non-JSON response behavior for this analysis repository.
---

# PNCP API Cartographer

Use this skill before changing collection logic or API assumptions.

## Workflow

1. Read `config/analysis.yaml` for base URLs, period, modality, CNPJs, and IBGE codes.
2. Validate endpoint behavior with small, targeted requests before changing code.
3. Prefer official OpenAPI specs:
   - `https://pncp.gov.br/pncp-consulta/v3/api-docs`
   - `https://pncp.gov.br/pncp-api/v3/api-docs`
4. Confirm modality code `6` through `https://pncp.gov.br/api/pncp/v1/modalidades`.
5. Treat HTTP 200 with `text/html` as a failed API response, not valid data.
6. For Sao Paulo, compare `cnpj=46395000000139` with `uf=SP` +
   `codigoMunicipioIbge=3550308`; note whether returned `orgaoEntidade.cnpj`
   differs from the matrix CNPJ.
7. For other capitals, check whether querying by matrix CNPJ captures the same
   municipal entity consistently enough to support the contrast.
8. Document any endpoint change in `README.md` and keep snapshots reproducible.

## Relevant Endpoints

- `GET /v1/contratacoes/publicacao`
- `GET /v1/orgaos/{cnpj}/compras/{ano}/{sequencial}`
- `GET /v1/orgaos/{cnpj}/compras/{ano}/{sequencial}/arquivos`
- `GET /v1/modalidades`

## Evidence to Preserve

- One representative API payload per capital.
- At least one Sao Paulo payload outside the CNPJ matrix, when available.
- Counts for matrix-CNPJ records, municipality-scan records, distinct CNPJs, and
  non-matrix CNPJ share.
