# Track: National archive coverage, updates and operations

Track ID: `nz_spatial_archive_operations_20260719`  
Phase: **NZ Spatial**  
Target release: **0.8.0**  
Maturity target: **M6**  
Stability class: **Operational**  
V1 critical: **yes**

## Goal

Scale the reference vertical slice into a maintained national archive with explicit automation, exceptions, freshness, backfill, coverage and preservation status.

## v1 role

This track is part of the stable v1 release contract. It is complete only when its implementation, compatibility, quality, security/governance, operational and reproducibility evidence satisfy both this specification and every applicable blocking gate in `conductor/releases.json` and `conductor/v1-gate.json`.

## Dependencies


- `nz_spatial_archive_mvp_20260718`
- `spatial_quality_temporality_20260718`
- `operations_preservation_sre_20260719`
- `nz_spatial_source_registry_20260718`

## Scope

- Connector rollout for all permitted machine-readable authority sources.
- Scheduled snapshots, delta capture, backfills, schema drift and exception management.
- National coverage, freshness, legal-status, rights and quality reporting.
- Storage partitioning, retention, preservation copies and cost/capacity management.
- Correction, supersession, deprecation and source retirement.

## Out of scope

- Claiming that every authority has equivalent data or historical depth.
- Automating restricted/viewer-only sources without permission.

## Requirements

- **R01.** Every authority/source has an operational disposition and named owner or exception.
- **R02.** Source-specific schedules reflect actual update patterns and service constraints.
- **R03.** Backfilled history is marked as reconstructed and never presented as contemporaneous capture.
- **R04.** Coverage metrics are multidimensional rather than a single national percentage.
- **R05.** Operational archives remain rebuildable from preserved raw evidence and code.

## Acceptance criteria

- [ ] Every current authority has a coverage and operational disposition.
- [ ] Every permitted machine-readable source is automated or has a documented, reviewed exception and remediation path.
- [ ] Scheduled operations meet published freshness, capture, release and fixity SLOs for the beta evidence period.
- [ ] Schema/service changes are detected, quarantined and resolved without silently corrupting canonical data.
- [ ] National releases publish coverage by authority, layer type, time depth, legal status, rights and quality.
- [ ] Retention, preservation, restore and correction procedures pass national-scale exercises.

## Hardening and maturity gates

- M2 requires executable proof, negative tests and traceable evidence; interfaces may remain experimental.
- M3 requires real-data integration, migration evidence and representative failure handling.
- M4 requires repeated operation, external use, SLO evidence and bounded compatibility changes.
- M5 requires frozen interfaces, independent review, security/performance/recovery qualification and release-candidate soak.
- M6 requires supported compatibility, signed and preserved releases, external reproduction, named maintainers and post-release verification.
- Exceptions must be machine-readable, scoped, approved, time-limited and visible in release evidence.

## Evidence required

- National source/connector coverage matrix.
- Rolling SLO, freshness, quality and exception reports.
- Backfill/reconstruction and schema-drift incident evidence.
- National-scale preservation, restore and cost/capacity report.

## Risks

- National scale multiplies fragile source dependencies.
- A coverage percentage hides missing high-impact layers.
- Backfills overwhelm services or storage.
- Local-government change leaves orphaned schedules or identifiers.

## Completion rule

The track may enter `complete` only after every acceptance criterion is evidenced in `index.md`, all blocking dependencies are complete, required migrations and documentation are published, and the target release readiness evaluator reports no track-specific blocker.
