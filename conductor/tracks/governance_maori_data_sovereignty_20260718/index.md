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

## Blocking defects

- None recorded.

## Decisions, exceptions and limitations

- None recorded.

## Review and handover

Required reviewer roles: Governance reviewer, Security reviewer, Data steward, Scientific reviewer.

Implementation is active. Evidence must be immutable or version-addressed, independently reviewed where required, and sufficient for the applicable release gates.
