# Track: Foundation architecture and programme governance

Track ID: `foundation_architecture_20260718`  
Phase: **Foundation**  
Target release: **0.3.0**  
Maturity target: **M6**  
Stability class: **Governance**  
V1 critical: **yes**

## Goal

Ratify the v1 product boundary, federated responsibility model, version axes, decision rights, release train and machine-checkable programme governance.

## v1 role

This track is part of the stable v1 release contract. It is complete only when its implementation, compatibility, quality, security/governance, operational and reproducibility evidence satisfy both this specification and every applicable blocking gate in `conductor/releases.json` and `conductor/v1-gate.json`.

## Dependencies


- None.

## Scope

- Federated connector, archive, domain, analytics and applied-research boundaries.
- Independent versioning for software, schemas, ontology, datasets, models and research objects.
- Architecture decisions, change control, ownership, release authority and exception handling.
- Machine-readable maturity levels, release gates, track dependencies and evidence expectations.
- Sustainability, contributor, maintainer and succession expectations for a supported 1.x line.

## Out of scope

- Selecting one mandatory database, graph engine or cloud provider.
- Declaring legal, clinical or operational authority for downstream applications.

## Requirements

- **R01.** Every component has one authoritative responsibility and a documented source-of-truth boundary.
- **R02.** Every normative contract has a version owner, compatibility policy and migration path.
- **R03.** Programme decisions and exceptions are recorded as versioned ADRs or release evidence.
- **R04.** The critical path permits synthetic solver and interface work to proceed in parallel with data acquisition.
- **R05.** The stable release boundary distinguishes platform guarantees from dataset coverage and applied-study claims.

## Acceptance criteria

- [ ] All architecture decisions are accepted, superseded or explicitly deferred with rationale and owner.
- [ ] Every v1-critical track has a repository owner, dependencies, target release, maturity target and checkable evidence contract.
- [ ] The track and release dependency graphs are acyclic and validated automatically.
- [ ] The v1 scope, non-claims, compatibility contract, support window and release authority are approved.
- [ ] At least two independent analysts complete an architecture review; analysts may be maintainers or agents. Each analyst must have a distinct identity, scope or method, and findings must be resolved or recorded.
- [ ] A contributor can regenerate the issue graph and roadmap status from a clean checkout.

## Hardening and maturity gates

- M2 requires executable proof, negative tests and traceable evidence; interfaces may remain experimental.
- M3 requires real-data integration, migration evidence and representative failure handling.
- M4 requires repeated operation, external use, SLO evidence and bounded compatibility changes.
- M5 requires frozen interfaces, independent review, security/performance/recovery qualification and release-candidate soak.
- M6 requires supported compatibility, signed and preserved releases, external reproduction, named maintainers and post-release verification.
- Exceptions must be machine-readable, scoped, approved, time-limited and visible in release evidence.

## Evidence required

- Accepted ADR set and architecture diagrams.
- Automated roadmap validation report and generated issue graph.
- Maintainer/reviewer decisions and unresolved-decision register.
- Published v1 scope, compatibility and sustainability policies.

## Risks

- Architecture becomes too abstract to test against real data.
- Repository boundaries are split before interfaces survive two real use cases.
- A nominal v1 is declared without operational or support commitments.

## Completion rule

The track may enter `complete` only after every acceptance criterion is evidenced in `index.md`, all blocking dependencies are complete, required migrations and documentation are published, and the target release readiness evaluator reports no track-specific blocker.
