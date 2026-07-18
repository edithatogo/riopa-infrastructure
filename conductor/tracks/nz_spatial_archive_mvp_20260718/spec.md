# Track: New Zealand Spatial Archive minimum viable release

Track ID: `nz_spatial_archive_mvp_20260718`  
Phase: **NZ Spatial**

## Goal

Publish a small but complete, temporally versioned spatial research object using heterogeneous national and council sources.

## Dependencies

- `nz_spatial_source_registry_20260718`
- `methods_research_objects_20260718`

## Scope

- Faithful raw capture and change detection for selected sources.
- Canonical spatial entities and bitemporal versions.
- GeoParquet, DuckDB Spatial and STAC/metadata materialisations.
- Quality, rights, methods, citation and attestation bundle.
- Prospective scheduled snapshots.

## Out of scope

- Immediate full national historical backfill.
- Facility optimisation before data quality gates pass.

## Acceptance criteria

- [ ] The release contains at least one LINZ/Stats national layer and zone/overlay layers from four heterogeneous councils.
- [ ] Raw source evidence and service metadata are preserved or resolvably referenced.
- [ ] All vector outputs pass geometry/schema and source-count reconciliation checks.
- [ ] A clean environment rebuild reaches declared R2 or higher.
- [ ] A DOI-ready RO-Crate and generated methods supplement are produced.

## Risks

- Large payload/storage cost.
- Unclear statutory status.
- Geometry/schema drift between councils.
