# Track: New Zealand spatial source and authority registry

Track ID: `nz_spatial_source_registry_20260718`  
Phase: **NZ Spatial**  
Target release: **0.4.0**  
Maturity target: **M6**  
Stability class: **Operational**  
V1 critical: **yes**

## Goal

Create a versioned national inventory of authorities, plans, GIS/ePlan services, documents, source status, rights, update evidence and connector readiness.

## v1 role

This track is part of the stable v1 release contract. It is complete only when its implementation, compatibility, quality, security/governance, operational and reproducibility evidence satisfy both this specification and every applicable blocking gate in `conductor/releases.json` and `conductor/v1-gate.json`.

## Dependencies


- `canonical_domain_schemas_ontology_20260719`
- `provenance_profile_v1_20260718`

## Scope

- Current and historical national, regional, territorial and unitary authority identities.
- District/regional plan, ePlan, GIS, ArcGIS, WFS, Koordinates, document and Gazette source records.
- LINZ, Stats NZ, MfE/planning standards, legislation and other national source families.
- Rights, statutory/informational status, update pattern, capability and health evidence.
- Machine-readable coverage, unresolved-source and connector-readiness classifications.

## Out of scope

- Assuming that every council exposes a machine-readable or redistributable layer.
- Interpreting plan provisions or declaring legal effect.

## Requirements

- **R01.** Every current authority has a registry record even when no reusable source is found.
- **R02.** Historical authority and source identities are retained rather than overwritten.
- **R03.** Discovery evidence is timestamped and distinguishes automated, manual and inferred findings.
- **R04.** Rights, access and legal-status uncertainties are explicit.
- **R05.** Registry snapshots are immutable and changes produce source events.

## Acceptance criteria

- [ ] Every current local and regional authority has authority, plan, service/document and disposition records.
- [ ] All named national source families are registered with access, rights, update and preservation evidence.
- [ ] Automated discovery adapters and manual review produce equivalent canonical records.
- [ ] Coverage reports distinguish available, restricted, viewer-only, document-only, unresolved and absent sources.
- [ ] Source changes, disappearances and terms/licence changes are detected and versioned.
- [ ] The registry is independently sampled and errors are below an approved threshold or transparently reported.

## Hardening and maturity gates

- M2 requires executable proof, negative tests and traceable evidence; interfaces may remain experimental.
- M3 requires real-data integration, migration evidence and representative failure handling.
- M4 requires repeated operation, external use, SLO evidence and bounded compatibility changes.
- M5 requires frozen interfaces, independent review, security/performance/recovery qualification and release-candidate soak.
- M6 requires supported compatibility, signed and preserved releases, external reproduction, named maintainers and post-release verification.
- Exceptions must be machine-readable, scoped, approved, time-limited and visible in release evidence.

## Evidence required

- Immutable registry snapshot and national coverage matrix.
- Discovery logs, capability snapshots and rights/status reviews.
- Independent sample audit and correction report.
- Connector readiness and unresolved-source backlog.

## Risks

- Council restructures or plan reforms invalidate authority identity.
- Viewer URLs are mistaken for open data services.
- Manual discovery becomes stale without ownership.
- A rights classification is copied across layers with different licences.

## Completion rule

The track may enter `complete` only after every acceptance criterion is evidenced in `index.md`, all blocking dependencies are complete, required migrations and documentation are published, and the target release readiness evaluator reports no track-specific blocker.
