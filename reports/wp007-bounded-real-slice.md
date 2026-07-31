# WP-007 bounded real-source slice

Captured on 31 July 2026, this evidence package exercises four public New
Zealand source roles without credentials and without publication:

| Role | Preserved source | Bound |
|---|---|---|
| LINZ | NZ Primary Parcels layer 50772 metadata and its CC BY 4.0 licence text | metadata only; no parcel features or ownership data |
| Council GIS | Wellington City 2024 District Plan Zones | `OBJECTID=1`, one polygon |
| Planning | Ministry for the Environment National Planning Standards, updated 2022 | one official PDF |
| Facility | Ministry of Health certified public-hospital providers | one official CSV snapshot |

The content-addressed HTTP objects and redacted request/response receipts are
under `evidence/wp007-real-slice/store`. The WCC capture set reconciles the
one-feature count before and after retrieval. Its canonical output is preserved
as GeoParquet and DuckDB with a machine-readable quality report. The evidence
manifest binds those capture IDs to the transformation, CRS, rights sources,
limitations, and explicit `not-attempted` publication state.

`uv run python scripts/verify_wp007_slice.py` checks the manifest hash, registry,
HTTP status, object sizes and hashes, source identities, PDF/CSV content types,
GeoParquet and DuckDB hashes and row counts, and a clean GeoParquet rebuild from
the frozen ArcGIS capture.

This is deliberately not a release or a complete track:

- LINZ payload acquisition still requires a selected layer workflow and, for
  native LDS services, an account/API key.
- One WCC feature is pipeline evidence, not council coverage or statutory
  interpretation.
- No spatial-to-provision legal link is asserted.
- The hospital register is not a multi-source reconciled facility model.
- WCC and Ministry of Health publisher rights pages were reviewed, but their
  servers rejected the pinned capture client with HTTP 403; their authoritative
  URLs remain referenced rather than bundled.
- No independent reproduction, target-specific publication review, DOI,
  attestation, or preservation deposit has occurred.
