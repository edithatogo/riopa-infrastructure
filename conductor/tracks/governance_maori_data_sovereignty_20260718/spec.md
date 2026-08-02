# Track: Rights, privacy and scope-triggered data governance framework

Track ID: `governance_maori_data_sovereignty_20260718`  
Phase: **Foundation**  
Target release: **0.3.0**  
Maturity target: **M6**  
Stability class: **Governance**  
V1 critical: **yes**

## Goal

Embed lawful reuse, privacy, safety, social licence and withdrawal decisions into source registration, analysis and publication gates. Cultural or community-specific review is triggered only when the documented scope, source terms or risk assessment requires it.

## v1 role

This track is part of the stable v1 release contract. It is complete only when its implementation, compatibility, quality, security/governance, operational and reproducibility evidence satisfy both this specification and every applicable blocking gate in `conductor/releases.json` and `conductor/v1-gate.json`.

## Dependencies


- `foundation_architecture_20260718`

## Scope

- Source access, licensing, attribution, redistribution and statutory-authority review.
- Data classification for public, restricted, sensitive, controlled and prohibited material.
- Scope-triggered cultural or community review, benefit and harm assessment.
- Privacy, ethics, safety, culturally sensitive geography and derived-data risk.
- Correction, withdrawal, supersession, takedown and benefit-sharing pathways.

## Out of scope

- Software claiming to certify consent, legal compliance or community approval.
- Publishing restricted health or operational unit-record data through the public archive.

## Requirements

- **R01.** Rights and governance status travel with sources, artifacts, transformations and releases.
- **R02.** Public visibility is never treated as permission to redistribute or infer.
- **R03.** Governance triggers can block capture, transformation, linkage, analysis or publication independently.
- **R04.** Agent-panel review decisions identify analyst role, evidence, date, expiry and scope.
- **R05.** Derived products are reviewed for new harms even when inputs are individually open.

## Acceptance criteria

- [ ] A versioned decision framework covers rights, privacy, ethics, scope-triggered cultural or community review, safety and legal-status triggers.
- [ ] Publication fails closed when required rights or governance decisions are unresolved.
- [ ] Controlled and public pathways are technically separated and tested.
- [ ] Correction, withdrawal and supersession drills preserve provenance while stopping inappropriate distribution.
- [ ] Every applied pilot has a documented benefit, harm, equity and governance review.

## Hardening and maturity gates

- M2 requires executable proof, negative tests and traceable evidence; interfaces may remain experimental.
- M3 requires real-data integration, migration evidence and representative failure handling.
- M4 requires repeated operation, external use, SLO evidence and bounded compatibility changes.
- M5 requires frozen interfaces, independent review, security/performance/recovery qualification and release-candidate soak.
- M6 requires supported compatibility, signed and preserved releases, external reproduction, named maintainers and post-release verification.
- Exceptions must be machine-readable, scoped, approved, time-limited and visible in release evidence.

## Evidence required

- Governance decision schema and trigger matrix.
- Rights inventories, review records and publication decisions.
- Controlled/public architecture tests and withdrawal exercise.
- Optional engagement guidance and benefit/harm records where applicable to the declared data scope.

## Risks

- Governance is reduced to a checklist without relationships or accountability.
- Open-data assumptions launder restrictions into derived releases.
- Granular geography or health linkage creates new group harms.
- A public withdrawal removes evidence needed to explain prior releases.

## Completion rule

The track may enter `complete` only after every acceptance criterion is evidenced in `index.md`, all blocking dependencies are complete, required migrations and documentation are published, and the target release readiness evaluator reports no track-specific blocker.
