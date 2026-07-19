# Track: New Zealand Spatial Archive real-data vertical slice

Track ID: `nz_spatial_archive_mvp_20260718`  
Phase: **NZ Spatial**  
Target release: **0.5.0**  
Maturity target: **M6**  
Stability class: **Reference**  
V1 critical: **yes**

## Goal

Publish a complete, temporally explicit spatial and planning research object using heterogeneous national and council sources, from raw evidence to portable materialisations.

## v1 role

This track is part of the stable v1 release contract. It is complete only when its implementation, compatibility, quality, security/governance, operational and reproducibility evidence satisfy both this specification and every applicable blocking gate in `conductor/releases.json` and `conductor/v1-gate.json`.

## Dependencies


- `connector_runtime_capture_20260719`
- `nz_spatial_source_registry_20260718`
- `methods_research_objects_20260718`
- `canonical_domain_schemas_ontology_20260719`

## Scope

- At least four deliberately heterogeneous council acquisition mechanisms.
- Relevant LINZ and Stats NZ reference layers and population/boundary evidence.
- Immutable raw captures, canonical bitemporal features and plan/document identities.
- GeoParquet and DuckDB Spatial materialisations with query examples.
- Quality, rights, coverage, methods and research-object release evidence.

## Out of scope

- Claiming complete national coverage in the MVP.
- Treating extracted plan interpretations as legal advice.

## Requirements

- **R01.** Council selection is justified by heterogeneity rather than convenience.
- **R02.** Raw, canonical and materialised layers are independently identifiable and linked.
- **R03.** Source publication, retrieval, valid, operative and superseded times are not conflated.
- **R04.** Geometry repair never replaces or hides original geometry.
- **R05.** Every materialisation declares fidelity losses and can be rebuilt from the named snapshot.

## Acceptance criteria

- [ ] Four heterogeneous councils and at least two national source families complete capture-to-release.
- [ ] Canonical features carry source identity, version identity, geometry digest and temporal assertions.
- [ ] GeoParquet and DuckDB Spatial rebuild deterministically and pass cross-tool query tests.
- [ ] Quality and coverage reports expose missing, unresolved, non-statutory and legally uncertain content.
- [ ] A complete externally validated research object and methods supplement are produced.
- [ ] A second clean environment reproduces the snapshot or documents tolerance-equivalent differences.

## Hardening and maturity gates

- M2 requires executable proof, negative tests and traceable evidence; interfaces may remain experimental.
- M3 requires real-data integration, migration evidence and representative failure handling.
- M4 requires repeated operation, external use, SLO evidence and bounded compatibility changes.
- M5 requires frozen interfaces, independent review, security/performance/recovery qualification and release-candidate soak.
- M6 requires supported compatibility, signed and preserved releases, external reproduction, named maintainers and post-release verification.
- Exceptions must be machine-readable, scoped, approved, time-limited and visible in release evidence.

## Evidence required

- Real raw/canonical/materialisation snapshot manifests.
- Council heterogeneity and selection report.
- Spatial/temporal quality, rights and coverage reports.
- External research-object validation and clean rebuild report.

## Risks

- Pilot councils are unrepresentative of national complexity.
- Large payloads make packaging or preservation impractical.
- Spatial layers and plan text disagree.
- Temporal evidence is incomplete and silently imputed.

## Completion rule

The track may enter `complete` only after every acceptance criterion is evidenced in `index.md`, all blocking dependencies are complete, required migrations and documentation are published, and the target release readiness evaluator reports no track-specific blocker.
