# Plan: operations_preservation_sre_20260719

## 1. Operational model and SLOs

- [x] 1.1 Define job state, retry, idempotency, quarantine and partial-failure semantics. Evidence: `schemas/operations-control.schema.json`, `docs/operations-control-contract-20260822.json`, `src/riopa_provenance/retry.py`, `tests/test_retry.py`. (f6e50d7)
- [x] 1.2 Define SLIs/SLOs, maintenance windows, upstream exclusions and alert thresholds. Evidence: `schemas/operations-control.schema.json`, `docs/operations-control-contract-20260822.json`, `docs/operations-slo.md`, `tests/test_operations_control_contract.py`. (f6e50d7)
- [x] 1.3 Define incident severity, escalation, communication and review. Evidence: `schemas/operations-control.schema.json`, `docs/operations-control-contract-20260822.json`, `tests/test_operations_control_contract.py`. (f6e50d7)

## 2. Observability and runbooks

- [ ] 2.1 Instrument source health, freshness, quality, storage, cost and release status.
- [ ] 2.2 Implement alerts with actionable ownership and suppression rules.
- [ ] 2.3 Write and test source, schema, rights, corruption and capacity runbooks.

## 3. Preservation and recovery

- [ ] 3.1 Define retention, replicas, fixity cadence and preservation package format.
- [ ] 3.2 Automate backup, restore, correction, supersession and withdrawal paths.
- [ ] 3.3 Conduct restore and disaster-recovery exercises.
- [x] 3.4 Define content-addressed multi-target replication with GitHub Actions, Hugging Face and Zenodo contingencies. (`docs/evidence-redundancy-plan-20260805.json`, `scripts/build_redundancy_manifest.py`)
- [x] 3.5 Generate a digest manifest for every hosted evidence bundle and expose pending target acceptance explicitly. (`tests/test_redundancy_manifest.py`)
- [ ] 3.6 Configure repository credentials and verify independent Hugging Face and Zenodo acceptance receipts.

## 4. Beta operation and stable gate

- [ ] 4.1 Operate the release pipeline for the required beta evidence period.
- [ ] 4.2 Publish SLO, incident, capacity and preservation reports.
- [ ] 4.3 Approve stable operational risk and support obligations.
- [x] 4.4 Start the protected-main cumulative daily beta campaign with a fail-closed hash-chained ledger. (`docs/operational-beta-observation-20260802.json`)

## Review fixes

- [x] R1 Constrain lifecycle transition endpoints to the declared job states and add a negative validation. Evidence: `schemas/operations-control.schema.json`, `tests/test_operations_control_contract.py`. (3af81f0)

## Track closeout

- [ ] C.1 Link implementation, test, review, migration and release evidence in `index.md`.
- [ ] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [ ] C.4 Update metadata status and target-release evidence through the Conductor workflow.
