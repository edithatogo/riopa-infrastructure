# Evidence index: Foundation architecture and programme governance

- **Track ID:** `foundation_architecture_20260718`
- **Status:** `validating`
- **Target release:** `0.3.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Governance`
- **Risk / priority:** `High` / `P0`
- **V1 critical:** `yes`
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Programme owner

Closeout sequence: `docs/foundation-provenance-connector-ontology-closeout-plan.md`.
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/14

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| R01–R03 | ADR reconciliation register | `docs/adr/README.md` | Accepted or explicitly deferred for the bounded M1 baseline; later qualification gates remain open |
| R01, R02, R05 | Scope, responsibility and compatibility boundary | `docs/v1-scope-and-boundaries.md`, `docs/architecture.md`, `docs/v1-release-policy.md` | Ratified as the bounded M1 development baseline; no stable-release approval implied |
| R03, R05 | Governance, decision rights and sustainability contract | `docs/governance-and-sustainability.md` | Ratified for M1 operation; named stable-release approvals remain pending |
| R01, R02, R03 | Executable roadmap, issue-graph and architecture-fitness validation | `src/riopa_provenance/roadmap.py`, `tests/test_roadmap_hardening.py`, `project/issues.yaml`, `reports/quality-baseline-inventory.md` | Clean locked runtime, complete suite, roadmap, quality and reproducibility validation pass locally |
| R02 | Normative contract ownership and migration matrix | `docs/contract-ownership-matrix.md` | Implemented; executable suite passes locally |
| R03, R05 | Independent analyst review records | `docs/architecture-reviews/2026-07-29-architecture-contract-analyst-01.md`, `docs/architecture-reviews/2026-07-29-architecture-governance-analyst-02.md` | Two records complete; findings resolved for M1 or explicitly deferred to named later gates |
| R01–R05 | Programme-owner bounded architecture ratification | `docs/architecture-baseline-ratification.md`; source revision `64c4dd7c28d18f1ed68f28a52421770777f92d7d` | M1 development baseline ratified on 2026-08-01; M2-M6 maturity and release approvals explicitly excluded |
| R05 | External dependency and release-gate register | `docs/external-dependency-register.md` | Current hosted checks are recorded as passed; independent reproduction, source authority, preservation and release authority remain open with explicit fallbacks |
| C.3 | M1 closeout audit | `docs/architecture-reviews/2026-08-01-foundation-closeout-audit.md` | Repository-owned blocker, waiver and limitation checks pass; later maturity and external gates remain open |
| M2-prep | Executable acceptance checklist | `docs/architecture-reviews/foundation-m2-evidence-checklist.md` | Defines bounded proof and explicit non-claims for the next maturity gate |
| M2-READINESS-20260801 | Machine-readable M2 readiness and later-gate boundary | `docs/foundation-maturity-readiness-20260801.json` | Repository-owned M2 preparation passes; promotion remains false |
| `FOUNDATION-AGENT-PANEL-WORDING-20260825` | Single-developer repository wording correction for agent-panel coverage | `docs/foundation-agent-panel-wording-correction-20260825.json` | Agent panels are repository assessors only; external participation, elapsed evidence and accountable authority remain separate gates |

## Blocking maturity gates

- M2 executable proof, negative tests and traceable evidence.
- M3 real-data integration and representative failure handling.
- M4 repeated operation, external use and SLO evidence.
- M5 orchestrated agent-panel qualification, recovery qualification and RC soak.
- M6 supported compatibility, external reproduction, named maintainers and stable release authority.

The consolidated parent-track maturity inventory is recorded in
`docs/parent-track-maturity-report-20260803.json`; it finds all 28 tracks at
M1 against an M6 target and does not promote any track.

## Decisions, exceptions and limitations

- ADR-0006, ADR-0009 and ADR-0011 are explicitly deferred with owners, revisit
  dates and follow-up tracks in `docs/adr/README.md`; they are not treated as
  approvals.
- The normative contract ownership and migration matrix is recorded in
  `docs/contract-ownership-matrix.md`.
- The programme-owner instruction ratifies only the M1 development architecture
  baseline. Named signatories, signed evidence and stable-release authority
  remain external M5/M6 gates.

## Review record

- Review scope: maturity-readiness and closeout changes through `601940f`.
- Finding: closeout task C.4 still described the track as `active` after the
  metadata and index moved to `validating`.
- Fix: aligned C.4 and the handover language with the validating status while
  retaining `promotion_ready: false` and the M2–M6 blockers.
- Validation: roadmap validation and repository test evidence are required
  before this review is closed; no external gate is represented as complete.

## Review and handover

Required analyst coverage: distinct agent-panel lenses with separate scopes and recorded dispositions; governance, API/schema and external-user perspectives remain recommended coverage. Agent panels assess repository evidence only and do not substitute for factual external participation or accountable release authority.

The programme-wide 2026-08-26 policy records that this is a single-developer
repository: AI agents provide repository-owned advice, the sole developer
dispositions findings and remains accountable, and no second-human or external
participation is claimed without exact evidence.

The continuation-state repair makes the machine-local next-work packet fail
closed when every configured package is complete or blocked, uses the locked
Python 3.14 environment for Make targets and refreshes the tracked roadmap
summary without changing track maturity or release readiness.

The bounded M1 architecture baseline is ratified; implementation remains
validating at M1. Evidence must be immutable or version-addressed, qualified by
the orchestrated agent panel where required, and sufficient for each later maturity and release gate.

Target-release metadata and evidence were revalidated on 2026-08-01; status is
`validating` by design until M2–M6 gates are evidenced.
