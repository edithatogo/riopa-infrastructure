# Evidence index: Foundation architecture and programme governance

- **Track ID:** `foundation_architecture_20260718`
- **Status:** `active`
- **Target release:** `0.3.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Governance`
- **Risk / priority:** `High` / `P0`
- **V1 critical:** `yes`
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Programme owner
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/14

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| R01–R03 | ADR reconciliation register | `docs/adr/README.md` | Implemented; ratification review pending |
| R01, R02, R05 | Scope, responsibility and compatibility boundary | `docs/v1-scope-and-boundaries.md`, `docs/architecture.md`, `docs/v1-release-policy.md` | Implemented; ratification review pending |
| R03, R05 | Governance, decision rights and sustainability contract | `docs/governance-and-sustainability.md` | Implemented; named approvals pending |
| R01, R02, R03 | Executable roadmap, issue-graph and architecture-fitness validation | `src/riopa_provenance/roadmap.py`, `tests/test_roadmap_hardening.py`, `project/issues.yaml`, `reports/quality-baseline-inventory.md` | Clean locked runtime, complete suite, roadmap, quality and reproducibility validation pass locally |
| R02 | Normative contract ownership and migration matrix | `docs/contract-ownership-matrix.md` | Implemented; executable suite passes locally |
| R03, R05 | Independent analyst review records | `docs/architecture-reviews/2026-07-29-architecture-contract-analyst-01.md`, `docs/architecture-reviews/2026-07-29-architecture-governance-analyst-02.md` | Two records complete; findings remain open |

## Blocking defects

- None recorded. Named ratification and publication remain track work rather
  than a concealed implementation blocker.

## Decisions, exceptions and limitations

- ADR-0006, ADR-0009 and ADR-0011 are explicitly deferred with owners, revisit
  dates and follow-up tracks in `docs/adr/README.md`; they are not treated as
  approvals.
- The normative contract ownership and migration matrix is recorded in
  `docs/contract-ownership-matrix.md`.

## Review and handover

Required analyst coverage: two independent analysts with distinct identities and scopes; governance, API/schema and external-user perspectives remain recommended coverage.

Implementation is active. Evidence must be immutable or version-addressed, independently reviewed where required, and sufficient for the applicable release gates.
