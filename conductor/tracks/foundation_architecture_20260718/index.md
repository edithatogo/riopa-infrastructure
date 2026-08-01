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

## Blocking defects

- None recorded. Named ratification and publication remain track work rather
  than a concealed implementation blocker.

## Decisions, exceptions and limitations

- ADR-0006, ADR-0009 and ADR-0011 are explicitly deferred with owners, revisit
  dates and follow-up tracks in `docs/adr/README.md`; they are not treated as
  approvals.
- The normative contract ownership and migration matrix is recorded in
  `docs/contract-ownership-matrix.md`.
- The programme-owner instruction ratifies only the M1 development architecture
  baseline. Named signatories, signed evidence and stable-release authority
  remain external M5/M6 gates.

## Review and handover

Required analyst coverage: two independent analysts with distinct identities and scopes; governance, API/schema and external-user perspectives remain recommended coverage.

The bounded M1 architecture baseline is ratified; implementation remains active
at M1. Evidence must be immutable or version-addressed, independently reviewed
where required, and sufficient for each later maturity and release gate.

Target-release metadata and evidence were revalidated on 2026-08-01; status
remains `active` by design until M2–M6 gates are evidenced.
