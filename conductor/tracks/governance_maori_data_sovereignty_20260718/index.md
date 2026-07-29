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
| R02, R03 | Fail-closed public/controlled decision core and tests | `src/riopa_provenance/governance.py`, `tests/test_governance.py` | Implemented; runtime suite pending environment provisioning |
| R01, R03 | Withdrawal and supersession record helpers | `src/riopa_provenance/governance.py`, `tests/test_governance.py` | Implemented; operational exercise pending |
| R04, R05 | Māori governance and engagement pathway | `docs/governance-engagement-pathway.md` | Implemented; live co-design/review not claimed |
| R05 | Applied benefit/harm/equity review instrument | `docs/applied-governance-review-template.md` | Template only; pilot decisions pending |

## Blocking defects

- `runtime-validation-provisioning`: locked dependency provisioning remains unavailable; runtime tests and schema validation are not yet executed in the complete environment.
- `maori-engagement-review`: no live co-design or appropriately engaged Māori governance review is claimed for this checkout.
- `withdrawal-drill-evidence`: correction/withdrawal helpers have unit-level contracts, but an end-to-end distribution reconciliation exercise is still required.

## Decisions, exceptions and limitations

- Public visibility is not permission to redistribute or infer; all unresolved decisions remain `review-required`.

## Review and handover

Required reviewer roles: Governance reviewer, Security reviewer, Data steward, Scientific reviewer.

Implementation is active. Evidence must be immutable or version-addressed, independently reviewed where required, and sufficient for the applicable release gates.
