# Evidence index: Stable v1 release hardening and general availability

- **Track ID:** `v1_release_hardening_20260719`
- **Status:** `active`
- **Target release:** `1.0.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Governance`
- **Risk / priority:** `Critical` / `P0`
- **V1 critical:** `yes`
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Release authority
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/139

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| V1-BASELINE-20260801 | Fail-closed stable-v1 readiness baseline | `docs/v1-release-readiness-baseline-20260801.json`, `tests/test_v1_release_readiness.py` | Repository checks passing; promotion explicitly blocked |

## Blocking defects

- Stable-v1 completion remains blocked by the gates listed in the readiness baseline, including external reproduction, user validation, operational soak, preserved signed release and release-authority decision.

## Decisions, exceptions and limitations

- None recorded.

## Review and handover

Required reviewer roles: Governance reviewer, API/schema reviewer, Provenance reviewer, Security reviewer, Data steward, Operations reviewer, Performance reviewer, Interoperability reviewer, Research-object reviewer, External user reviewer, Quantitative methods reviewer, Scientific reviewer.

This index records a bounded repository-owned readiness baseline while the track remains `active`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, independently reviewed where required, and sufficient for the applicable release gates.

## Review record

- Review scope: v1 readiness baseline, plan status, metadata and registry through
  `1bac0cc`.
- Finding: the baseline was incorrectly used as evidence that the complete
  normative API/schema/ontology inventory was finished.
- Fix: restored task 1.1 to pending and recorded the boundary explicitly.
