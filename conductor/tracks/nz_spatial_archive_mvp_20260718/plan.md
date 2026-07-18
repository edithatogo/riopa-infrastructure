# Plan: nz_spatial_archive_mvp_20260718

## 1. Capture

- [ ] 1.1 Implement selected connector capture and retry/change semantics.
- [ ] 1.2 Preserve service definitions and original distributions.
- [ ] 1.3 Emit capture events and rights evidence.

## 2. Canonical model

- [ ] 2.1 Create feature/version tables and source mappings.
- [ ] 2.2 Implement CRS, geometry repair and source-field preservation.
- [ ] 2.3 Create temporal assertions without inferring legal dates.

## 3. Materialise and validate

- [ ] 3.1 Build GeoParquet and DuckDB Spatial bundle.
- [ ] 3.2 Build STAC/catalogue views and example queries.
- [ ] 3.3 Run quality profile and independent rebuild.

## 4. Release

- [ ] 4.1 Generate research object, methods, citation and attestations.
- [ ] 4.2 Publish draft, review source rights/attribution, then DOI release.
- [ ] 4.3 Enable prospective scheduled snapshots and health monitoring.
