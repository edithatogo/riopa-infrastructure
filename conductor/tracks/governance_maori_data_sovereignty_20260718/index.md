# Evidence index: Rights, privacy and Māori data sovereignty framework

- **Track ID:** `governance_maori_data_sovereignty_20260718`
- **Status:** `active`
- **Target release:** `0.3.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Governance`
- **Risk / priority:** `Critical` / `P0`
- **V1 critical:** `yes`
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Programme owner
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/19

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| R01, R02, R04, R05 | Versioned governance decision framework and schema | `docs/governance-decision-framework.md`, `schemas/governance-decision.schema.json` | Implemented; runtime suite pending environment provisioning |
| R01 | Governance decision references on source, artifact, transformation, snapshot and release records | `schemas/source-record.schema.json`, `schemas/artifact.schema.json`, `schemas/transformation-run.schema.json`, `schemas/snapshot-manifest.schema.json`, `schemas/release-evidence.schema.json` | Implemented; runtime suite pending environment provisioning |
| R02, R03 | Fail-closed public/controlled decision core and tests | `src/riopa_provenance/governance.py`, `tests/test_governance.py` | Implemented; runtime suite pending environment provisioning |
| R01, R03 | Withdrawal and supersession record helpers | `src/riopa_provenance/governance.py`, `tests/test_governance.py` | Implemented; operational exercise pending |
| R04, R05 | Māori governance and engagement pathway | `docs/governance-engagement-pathway.md` | Implemented; live co-design/review not claimed |
| R05 | Applied benefit/harm/equity review instrument | `docs/applied-governance-review-template.md` | Template only; pilot decisions pending |
| R02, R03 | Synthetic withdrawal and public/controlled pathway drill | `reports/governance-withdrawal-drill.md` | Passed; live takedown/reconciliation not claimed |
| R04, R05 | Release and pilot governance audit | `reports/governance-release-pilot-audit.md` | No live pilots/releases approved; future scope explicitly bounded |
| R04 | Review fix for expiry and conflict handling | `src/riopa_provenance/governance.py`, `tests/test_governance.py` | Implemented; runtime suite pending environment provisioning |
| R05 | Planned facility, health, deprivation and culturally sensitive geography review | `reports/governance-use-case-review.md` | All remain `review-required`; no publication approval inferred |

## Blocking defects

- `runtime-validation-provisioning`: locked dependency provisioning remains unavailable; runtime tests and schema validation are not yet executed in the complete environment.
- `maori-engagement-review`: no live co-design or appropriately engaged Māori governance review is claimed for this checkout.
- `live-distribution-reconciliation`: local target reconciliation is tested, but no live distribution/takedown system is in scope for this checkout.

## Decisions, exceptions and limitations

- Public visibility is not permission to redistribute or infer; all unresolved decisions remain `review-required`.

## Review and handover

Required reviewer roles: Governance reviewer, Security reviewer, Data steward, Scientific reviewer.

Implementation is active. Evidence must be immutable or version-addressed, independently reviewed where required, and sufficient for the applicable release gates.
