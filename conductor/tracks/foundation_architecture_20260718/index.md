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
| R01, R02, R03 | Executable roadmap, issue-graph and architecture-fitness validation | `src/riopa_provenance/roadmap.py`, `tests/test_roadmap_hardening.py`, `project/issues.yaml` | Implemented; full runtime validation pending environment provisioning |
| R03, R05 | Architecture review packet | `docs/architecture-review-template.md` | Pending two maintainer/external review records |

## Blocking defects

- `review-runtime-provisioning`: full Python/pytest and roadmap validation cannot currently run because the locked dependency mirror is timing out (`webcolors==25.10.0`); retry when the mirror recovers.
- `review-approval-required`: two independent maintainer/external architecture reviews are required by the track acceptance criteria; no approval is inferred from this implementation.

## Decisions, exceptions and limitations

- None recorded.

## Review and handover

Required reviewer roles: Governance reviewer, API/schema reviewer, External user reviewer.

Implementation is active. Evidence must be immutable or version-addressed, independently reviewed where required, and sufficient for the applicable release gates.
