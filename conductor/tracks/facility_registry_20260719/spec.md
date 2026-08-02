# Track: Versioned multi-source facility registry

Track ID: `facility_registry_20260719`  
Phase: **Analytics**  
Target release: **0.6.0**  
Maturity target: **M6**  
Stability class: **Reference**  
V1 critical: **yes**

## Goal

Reconcile supermarkets, health services and other facilities from multiple public assertions while preserving disagreement, confidence, temporal history, geocoding and rights evidence.

## v1 role

This track is part of the stable v1 release contract. It is complete only when its implementation, compatibility, quality, security/governance, operational and reproducibility evidence satisfy both this specification and every applicable blocking gate in `conductor/releases.json` and `conductor/v1-gate.json`.

## Dependencies


- `canonical_domain_schemas_ontology_20260719`
- `connector_runtime_capture_20260719`

## Scope

- Facility, operator, location, service, opening/closure and source-assertion identities.
- Entity-resolution candidates, evidence, confidence, review and adjudication.
- Source and separately geocoded coordinates, uncertainty and positional quality.
- Facility type, service range, opening hours, capacity proxies and temporal changes.
- Rights, attribution, sensitive-service and governance classifications.

## Out of scope

- Treating any one commercial map or retailer locator as definitive.
- Publishing sensitive service locations or operational capacity where inappropriate.

## Requirements

- **R01.** Source assertions are immutable and remain separate from reconciled facility identities.
- **R02.** Matches expose features, score, method, model/version and human decision.
- **R03.** Relocations, rebrands, closures and temporary states do not overwrite history.
- **R04.** Coordinates retain provenance and positional uncertainty.
- **R05.** Facility classification is versioned and supports disputed/unknown states.

## Acceptance criteria

- [ ] At least three independent supermarket/food-retail source families and two health-service source families are represented where rights permit.
- [ ] Entity-resolution precision/recall or equivalent review metrics are reported on a stratified sample.
- [ ] Facility history represents opening, closure, relocation, rebrand and source disagreement.
- [ ] Source/geocoded coordinates and uncertainty are separately queryable.
- [ ] Manual adjudication records are reproducible and agent-panel/audit evidence is preserved.
- [ ] Public release filters sensitive/restricted facilities according to governance decisions.

## Hardening and maturity gates

- M2 requires executable proof, negative tests and traceable evidence; interfaces may remain experimental.
- M3 requires real-data integration, migration evidence and representative failure handling.
- M4 requires repeated operation, external use, SLO evidence and bounded compatibility changes.
- M5 requires frozen interfaces, orchestrated agent-panel qualification, security/performance/recovery qualification and release-candidate soak.
- M6 requires supported compatibility, signed and preserved releases, external reproduction, named maintainers and post-release verification.
- Exceptions must be machine-readable, scoped, approved, time-limited and visible in release evidence.

## Evidence required

- Facility assertion and reconciliation datasets.
- Match model, thresholds and stratified review report.
- Temporal change and coordinate-quality report.
- Rights/governance filtering tests.

## Risks

- Duplicate or misclassified facilities bias access estimates.
- A closure is mistaken for source disappearance.
- Geocoding shifts a facility across a meaningful boundary.
- Commercial terms prohibit redistribution of source assertions.

## Completion rule

The track may enter `complete` only after every acceptance criterion is evidenced in `index.md`, all blocking dependencies are complete, required migrations and documentation are published, and the target release readiness evaluator reports no track-specific blocker.
