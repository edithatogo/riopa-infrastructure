# Track: Repository template and cross-repository adoption

Track ID: `repository_template_adoption_20260718`  
Phase: **Core**  
Target release: **0.5.0**  
Maturity target: **M6**  
Stability class: **Platform**  
V1 critical: **yes**

## Goal

Make provenance-first setup, Conductor governance, CI, releases and staged adoption easy across existing and future repositories without destructive rewrites.

## v1 role

This track is part of the stable v1 release contract. It is complete only when its implementation, compatibility, quality, security/governance, operational and reproducibility evidence satisfy both this specification and every applicable blocking gate in `conductor/releases.json` and `conductor/v1-gate.json`.

## Dependencies


- `provenance_profile_v1_20260718`
- `methods_research_objects_20260718`
- `security_supply_chain_20260719`

## Scope

- Greenfield and brownfield repository scaffolding.
- Conductor files, track metadata, issue generation, CI, security and release workflows.
- Adapter templates for connectors, archives, transformations and analytics.
- Adoption levels from inventory through independent reproduction.
- Automated upgrade, drift detection and migration support.

## Out of scope

- Forcing all repositories into one language, build tool or deployment model.
- Deleting repository-native provenance or release artifacts.

## Requirements

- **R01.** The template is parameterised and minimally opinionated outside normative evidence contracts.
- **R02.** Brownfield adoption begins with evidence inventory and additive emission.
- **R03.** Generated files have ownership and safe regeneration boundaries.
- **R04.** Template upgrades are reviewable, reversible and tested against representative repositories.
- **R05.** Adoption status is evidence based, not self-declared.

## Acceptance criteria

- [ ] One command creates a valid greenfield repository with Conductor, CI, security, release and documentation baseline.
- [ ] Brownfield mode inventories and documents existing systems before proposing changes.
- [ ] At least three existing repositories reach dual-emission adoption, two package research objects and one is independently reproduced.
- [ ] Template upgrades detect drift and preserve approved local customisation.
- [ ] Contributor setup and release workflows pass documentation tests on Linux and one additional supported environment.
- [ ] Cross-repository issues, dependencies and evidence links remain synchronised.

## Hardening and maturity gates

- M2 requires executable proof, negative tests and traceable evidence; interfaces may remain experimental.
- M3 requires real-data integration, migration evidence and representative failure handling.
- M4 requires repeated operation, external use, SLO evidence and bounded compatibility changes.
- M5 requires frozen interfaces, independent review, security/performance/recovery qualification and release-candidate soak.
- M6 requires supported compatibility, signed and preserved releases, external reproduction, named maintainers and post-release verification.
- Exceptions must be machine-readable, scoped, approved, time-limited and visible in release evidence.

## Evidence required

- Template generation and upgrade test suite.
- Adoption matrix with repository CI/release evidence.
- Brownfield migration and rollback reports.
- Contributor journey and documentation test results.

## Risks

- Template complexity discourages small repositories.
- Generated changes overwrite local workflows.
- Adoption metrics reward superficial metadata emission.
- Cross-repository issue state drifts from Conductor.

## Completion rule

The track may enter `complete` only after every acceptance criterion is evidenced in `index.md`, all blocking dependencies are complete, required migrations and documentation are published, and the target release readiness evaluator reports no track-specific blocker.
