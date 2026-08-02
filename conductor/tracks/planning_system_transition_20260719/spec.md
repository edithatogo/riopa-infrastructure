# Track: Planning-system transition and legal continuity

Track ID: `planning_system_transition_20260719`  
Phase: **NZ Spatial**  
Target release: **0.7.0**  
Maturity target: **M6**  
Stability class: **Reference**  
V1 critical: **yes**

## Goal

Represent legislation, authority, plan and provision transitions so longitudinal analyses remain reproducible through planning reform, reorganisation and partial legal succession.

## v1 role

This track is part of the stable v1 release contract. It is complete only when its implementation, compatibility, quality, security/governance, operational and reproducibility evidence satisfy both this specification and every applicable blocking gate in `conductor/releases.json` and `conductor/v1-gate.json`.

## Dependencies


- `planning_rules_linkage_20260718`
- `canonical_domain_schemas_ontology_20260719`

## Scope

- Predecessor/successor legislation, authorities, planning instruments and provisions.
- Proposed, notified, operative, partly operative, appealed, superseded and transitional states.
- Continuity, replacement, split, merge and uncertain mapping relationships.
- Temporal crosswalks for longitudinal analysis and historical reconstruction.
- Change notes and source evidence without offering legal opinion.

## Out of scope

- Predicting future legislation or asserting court/consent outcomes.
- Collapsing transition uncertainty into a single effective date.

## Requirements

- **R01.** All transition claims cite official evidence and record when the archive learned them.
- **R02.** Authority and plan identity survive rename, merger, split and replacement.
- **R03.** Continuity mappings can be one-to-many, many-to-one, partial or unresolved.
- **R04.** Historical reconstruction distinguishes contemporaneous capture from later reconstruction.
- **R05.** Analyses can pin the legal/knowledge-time perspective used.

## Acceptance criteria

- [ ] Transition schemas represent all named legal and plan states without substituting retrieval time.
- [ ] At least one authority reorganisation and one plan replacement are reconstructed with evidence.
- [ ] Longitudinal queries can choose valid-time, recorded-time and as-known-at perspectives.
- [ ] Continuity crosswalks expose confidence, scope and non-equivalence.
- [ ] An orchestrated planning-domain agent panel confirms that the data model does not imply legal advice.
- [ ] Migration guidance covers future planning-system changes without rewriting historical records.

## Hardening and maturity gates

- M2 requires executable proof, negative tests and traceable evidence; interfaces may remain experimental.
- M3 requires real-data integration, migration evidence and representative failure handling.
- M4 requires repeated operation, external use, SLO evidence and bounded compatibility changes.
- M5 requires frozen interfaces, orchestrated agent-panel qualification, security/performance/recovery qualification and release-candidate soak.
- M6 requires supported compatibility, signed and preserved releases, external reproduction, named maintainers and post-release verification.
- Exceptions must be machine-readable, scoped, approved, time-limited and visible in release evidence.

## Evidence required

- Transition and continuity schema fixtures.
- Worked authority and plan transition reconstructions.
- Temporal query and crosswalk validation.
- Planning-domain agent-panel report and legal non-authority statement.

## Risks

- Reform creates concepts not anticipated by the model.
- Later reconstructions overwrite what was known contemporaneously.
- A continuity mapping is mistaken for legal equivalence.
- Source notices conflict or are corrected retroactively.

## Completion rule

The track may enter `complete` only after every acceptance criterion is evidenced in `index.md`, all blocking dependencies are complete, required migrations and documentation are published, and the target release readiness evaluator reports no track-specific blocker.
