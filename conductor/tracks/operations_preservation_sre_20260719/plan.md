# Plan: operations_preservation_sre_20260719

## 1. Operational model and SLOs

- [x] 1.1 Define job state, retry, idempotency, quarantine and partial-failure semantics. Evidence: `schemas/operations-control.schema.json`, `docs/operations-control-contract-20260822.json`, `src/riopa_provenance/retry.py`, `tests/test_retry.py`. (f6e50d7)
- [x] 1.2 Define SLIs/SLOs, maintenance windows, upstream exclusions and alert thresholds. Evidence: `schemas/operations-control.schema.json`, `docs/operations-control-contract-20260822.json`, `docs/operations-slo.md`, `tests/test_operations_control_contract.py`. (f6e50d7)
- [x] 1.3 Define incident severity, escalation, communication and review. Evidence: `schemas/operations-control.schema.json`, `docs/operations-control-contract-20260822.json`, `tests/test_operations_control_contract.py`. (f6e50d7)

## 2. Observability and runbooks

- [x] 2.1 Instrument source health, freshness, quality, storage, cost and release status. Evidence: `docs/operations-observability-contract-20260822.json`, `tests/test_operations_observability_contract.py`; measurements remain candidate-not-measured until hosted operations emit them.
- [x] 2.2 Implement alerts with actionable ownership and suppression rules. Evidence: `docs/operations-alert-contract-20260822.json`, `tests/test_operations_alert_contract.py`; deployment and notification receipts remain pending.
- [x] 2.3 Write and test source, schema, rights, corruption and capacity runbooks. Evidence: `docs/operations-runbook-catalog-20260822.json`, `docs/runbooks/*.md`, `tests/test_operations_runbook_catalog.py`; execution receipts remain pending.

## 3. Preservation and recovery

- [x] 3.1 Define retention, replicas, fixity cadence and preservation package format. Evidence: `docs/preservation-package-contract-20260822.json`, `tests/test_preservation_package_contract.py`; independent target acceptance and restore execution remain pending.
- [x] 3.2 Implement the repository recovery-successor contract for backup/restore, correction, supersession and withdrawal paths. Evidence: `docs/operations-recovery-successor-contract-20260824.json`, `tests/test_operations_recovery_successor_contract.py`; repository state-machine and negative validation pass, while executable provider backup/restore, disaster-recovery exercise and independent target acceptance remain pending. (evidence contract commit: `675ddbefa280ae234754b3f2d830235d5df324d2`)
- [x] 3.3 Define and validate restore/disaster-recovery exercise reports. Evidence: `docs/operations-dr-exercise-contract-20260824.json`, `src/riopa_provenance/recovery.py`, `tests/test_recovery.py`; report construction and failure-preservation validation pass, while actual production-representative execution remains pending. (contract commit: `437d50c1efcb883a95a3dcdf838f5c63624dcc32`)
- [x] 3.4 Define content-addressed multi-target replication with GitHub Actions, Hugging Face and Zenodo contingencies. (`docs/evidence-redundancy-plan-20260805.json`, `scripts/build_redundancy_manifest.py`)
- [x] 3.5 Generate a digest manifest for every hosted evidence bundle and expose pending target acceptance explicitly. (`tests/test_redundancy_manifest.py`)
- [x] 3.6 Validate the required GitHub Actions, Hugging Face and Zenodo acceptance-receipt shape against one exact bundle digest. The validator is repository-owned and does not create target receipts; credentials, factual target acceptance and preservation qualification remain open (`scripts/build_redundancy_manifest.py:validate_replication_receipts`, `docs/replication-receipt-validation-contract-20260825.json`).

## 4. Beta operation and stable gate

- [ ] 4.1 Operate the release pipeline for the required beta evidence period.
- [ ] 4.2 Publish SLO, incident, capacity and preservation reports.
- [ ] 4.3 Approve stable operational risk and support obligations.
- [x] 4.4 Start the protected-main cumulative daily beta campaign with a fail-closed hash-chained ledger. (`docs/operational-beta-observation-20260802.json`)
- [x] 4.6 Isolate scheduled, replay and exact-RC campaign runs by campaign, lane and candidate revision so unrelated runs cannot cancel one another. (`.github/workflows/evidence-campaign.yml`, `tests/test_campaign_v2.py`)
- [x] 4.7 Deduplicate identical receipt bytes restored under multiple artifact paths before calculating elapsed or cycle counts. (`scripts/build_campaign_ledger.py`, `tests/test_campaign_ledger.py`)
- [x] 4.8 Validate the checked-in campaign status snapshot for unique runs, exact RC binding and latest receipt revision before release readiness checks. (`scripts/validate_campaign_status.py`, `tests/test_campaign_status.py`, `scripts/ci_quality.sh`)
- [x] 4.5 Bind RC-soak execution to the supplied exact candidate revision so later documentation commits do not silently change the candidate. (`.github/workflows/evidence-campaign.yml`, `scripts/record_hosted_evidence.py`, `tests/test_campaign_v2.py`; the 30-day duration remains pending.)
- [x] 4.9 Bind scheduled protected-main observations to the current `github.sha` and derive revision-specific campaign/qualification identifiers so merges automatically reset elapsed segments (`docs/beta-campaign-schedule-hardening-20260829.json`, `.github/workflows/evidence-campaign.yml`, `tests/test_campaign_v2.py`).
- [x] 4.10 Verify the immutable public Hugging Face release mirror from an unauthenticated scheduled workflow, failing closed on receipt drift, HTTP errors or byte mismatches (`scripts/verify_hf_release_mirror.py`, `.github/workflows/verify-release-mirror.yml`, `docs/hf-release-mirror-verifier-20260829.json`, `tests/test_hf_release_mirror_verifier.py`). This improves redundancy observability but does not establish preservation acceptance or stable-v1 gates.

## Review fixes

- [x] R1 Constrain lifecycle transition endpoints to the declared job states and add a negative validation. Evidence: `schemas/operations-control.schema.json`, `tests/test_operations_control_contract.py`. (3af81f0)
- [x] R2 Record a bounded four-lens agent-panel qualification of operations, preservation and campaign controls without closing provider, elapsed, participant or authority gates (`docs/operations-panel-qualification-20260825.json`, `tests/test_operations_panel_qualification.py`).
- [x] R3 Reject malformed replication manifests, non-object receipts and duplicate target receipts before acceptance validation (`scripts/build_redundancy_manifest.py`, `tests/test_redundancy_manifest.py`).

## Track closeout

- [x] C.1 Link implementation, test, review, migration and release evidence in `index.md` for the repository-owned slice; hosted, preservation and elapsed gates remain explicitly pending.
- [x] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [x] C.4 Update metadata status and target-release evidence through the Conductor workflow; status remains `active`/M1 because the documented gates are unresolved.
