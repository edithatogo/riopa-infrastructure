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
- [x] 3.6 Validate the required GitHub Actions, Hugging Face and Zenodo acceptance-receipt shape against one exact bundle digest. The validator is repository-owned; successor receipts now prove public target acceptance for the exact `v0.4.0` release assets, while per-campaign bundles, the eventual stable candidate and provider-backed restore remain open (`scripts/build_redundancy_manifest.py:validate_replication_receipts`, `docs/replication-receipt-validation-contract-20260825.json`, `docs/v0.4.0-preservation-wp006-reconciliation-20260829.json`).

## 4. Beta operation and stable gate

- [ ] 4.1 Operate the release pipeline for the required beta evidence period.
- [ ] 4.2 Publish SLO, incident, capacity and preservation reports.
  - [x] Prepare a deterministic candidate-only report bundle with explicit pending states and content hashes (`scripts/build_operations_report_bundle.py`, `docs/operations-report-bundle-contract-20260829.json`, `tests/test_operations_report_bundle.py`). Factual hosted reports and publication remain pending.
- [ ] 4.3 Approve stable operational risk and support obligations.
- [x] 4.4 Start the protected-main cumulative daily beta campaign with a fail-closed hash-chained ledger. (`docs/operational-beta-observation-20260802.json`)
- [x] 4.6 Isolate scheduled, replay and exact-RC campaign runs by campaign, lane and candidate revision so unrelated runs cannot cancel one another. (`.github/workflows/evidence-campaign.yml`, `tests/test_campaign_v2.py`)
- [x] 4.7 Deduplicate identical receipt bytes restored under multiple artifact paths before calculating elapsed or cycle counts. (`scripts/build_campaign_ledger.py`, `tests/test_campaign_ledger.py`)
- [x] 4.8 Validate the checked-in campaign status snapshot for unique runs, exact RC binding and latest receipt revision before release readiness checks. (`scripts/validate_campaign_status.py`, `tests/test_campaign_status.py`, `scripts/ci_quality.sh`)
- [x] 4.5 Bind RC-soak execution to the supplied exact candidate revision so later documentation commits do not silently change the candidate. (`.github/workflows/evidence-campaign.yml`, `scripts/record_hosted_evidence.py`, `tests/test_campaign_v2.py`; the 30-day duration remains pending.)
- [x] 4.9 Bind scheduled protected-main observations to the current `github.sha` and derive revision-specific campaign/qualification identifiers so merges automatically reset elapsed segments (`docs/beta-campaign-schedule-hardening-20260829.json`, `.github/workflows/evidence-campaign.yml`, `tests/test_campaign_v2.py`).
- [x] 4.10 Verify the immutable public Hugging Face release mirror from an unauthenticated scheduled workflow, failing closed on receipt drift, HTTP errors or byte mismatches (`scripts/verify_hf_release_mirror.py`, `.github/workflows/verify-release-mirror.yml`, `docs/hf-release-mirror-verifier-20260829.json`, `tests/test_hf_release_mirror_verifier.py`). This improves redundancy observability but does not establish preservation acceptance or stable-v1 gates.
- [x] 4.11 Reconcile the anonymously verified Hugging Face mirror and Zenodo DOI as complete preservation evidence for the `v0.4.0` public technical preview only; retain stable-candidate replication, provider restore, elapsed-operation and authority gates (`docs/v0.4.0-preservation-wp006-reconciliation-20260829.json`, `tests/test_v040_preservation_wp006_reconciliation.py`).
- [x] 4.12 Require lowercase 40-character hexadecimal Git revisions in campaign status source, observation and RC bindings, with malformed-input regression coverage; hosted execution, elapsed, preservation and authority gates remain open (`scripts/validate_campaign_status.py`, `tests/test_campaign_status.py`, `docs/campaign-status-revision-validation-20260830.json`).
- [x] 4.13 Correct the known truncated run-32519141017 revision from the immutable hosted run head and record the predecessor correction explicitly (`docs/campaign-status-correction-20260830.json`).
- [x] 4.14 Extend strict revision validation to supplemental observation and candidate fields with negative coverage; supplemental records retain their non-qualifying semantics (`scripts/validate_campaign_status.py`, `tests/test_campaign_status.py`, `docs/campaign-status-revision-validation-20260830.json`).
- [x] 4.15 Require every supplemental observation to carry a strict revision while keeping candidate revision optional-but-validated; record an immutable successor evidence artifact (`scripts/validate_campaign_status.py`, `tests/test_campaign_status.py`, `docs/campaign-status-supplemental-revision-validation-20260830.json`).
- [x] 4.16 Record fresh hosted supplemental beta and exact-candidate RC observations with receipt/log digests; retain their technical-preview classification and all elapsed, recovery, external, preservation and authority gates (`docs/hosted-beta-rc-campaign-observation-20260829-ddec941.json`, runs 33259405506/33259407593).
- [x] 4.17 Record the fresh hosted control-matrix supplemental drills with receipt/log digests; retain their technical-preview classification and all elapsed, production-recovery, national-scale, external, preservation and authority gates (`docs/hosted-control-matrix-observation-20260829-3b2fbf4.json`, runs 33259809069/33259810861/33259813004/33259815211/33259817003).
- [x] 4.18 Record the fresh hosted supplemental operational-observation drill with receipt/log digests; retain its technical-preview classification and do not advance beta/RC elapsed clocks or close recovery, national-scale, external, preservation or authority gates (`docs/hosted-supplemental-operational-observation-20260830-692545e.json`, run 33260680164).
- [x] 4.19 Record the fresh hosted supplemental recovery-rollback drill with receipt/log digests; retain its technical-preview classification and do not advance beta/RC elapsed clocks or close production-recovery, national-scale, external, preservation or authority gates (`docs/hosted-supplemental-recovery-observation-20260830-92b405c.json`, run 33261028041).
- [x] 4.20 Record the fresh hosted architecture-diverse supplemental performance rehearsal with both receipt/log digest pairs; the receipts are from one workflow run and are identified by `x86_64` and `arm64`; retain its technical-preview classification and do not advance beta/RC elapsed clocks or close national-scale, production-recovery, external, preservation or authority gates (`docs/hosted-supplemental-performance-observation-20260830-31e304a.json`, run 33261328505).
- [x] 4.21 Record the fresh hosted supplemental scale-smoke drill with receipt/log digests; retain its technical-preview classification and do not advance beta/RC elapsed clocks or close national-scale, production-recovery, external, preservation or authority gates (`docs/hosted-supplemental-scale-observation-20260830-9632c56.json`, run 33261927414).
- [x] 4.22 Record the fresh hosted supplemental agent-clean-room rehearsal with receipt/log digests; retain its technical-preview classification and do not advance beta/RC elapsed clocks or close independent reproduction, production-recovery, national-scale, preservation or authority gates (`docs/hosted-supplemental-cleanroom-observation-20260830-17aaec8.json`, run 33262213373).
- [x] 4.23 Record the fresh hosted supplemental agent-user workflow rehearsal with raw receipt/log paths; retain its technical-preview classification, do not treat it as external participant evidence, and do not advance beta/RC elapsed clocks or close production-recovery, national-scale, preservation or authority gates (`docs/hosted-supplemental-agent-user-observation-20260830-b97b6f9.json`, run 33262456945).
- [x] 4.24 Record the fresh hosted supplemental exact-RC rehearsal with raw receipt/log paths; retain its technical-preview classification and do not advance the exact-RC elapsed clock or close production-recovery, external operator/user, preservation or authority gates (`docs/hosted-supplemental-rc-observation-20260830-26bc0b4.json`, run 33262668117).
- [x] 4.25 Record the fresh hosted supplemental retrospective replay with raw receipt/log paths; retain its retrospective classification and do not advance beta/RC elapsed clocks or close external, national-scale, production-recovery, preservation or authority gates (`docs/hosted-supplemental-retrospective-observation-20260830-26bc0b4.json`, run 33263289821).
- [x] 4.26 Separate current campaign qualification tooling from the exact candidate checkout so qualifying receipts retain activation/classification and candidate tests remain content-addressed; validate workflow ordering and fail-closed ledger controls (`.github/workflows/evidence-campaign.yml`, `tests/test_campaign_v2.py`, `docs/campaign-qualification-tooling-fix-20260830.json`). Hosted activation, elapsed, recovery, scale, external, preservation and authority gates remain open.
- [x] 4.27 Activate clean beta/RC campaign identifiers after excluding prior technical-preview and retrospective receipts; preserve the first qualifying observations and record the reset boundary (`docs/campaign-qualification-activation-20260830.json`, runs 33289129127/33289130323). Duration, cycle, recovery, scale, external, preservation and authority gates remain open.

## Review fixes

- [x] R6 Validate operations report bundles by self-digest, exact component
  categories, candidate/pending statuses and explicit nonclaims
  (`scripts/build_operations_report_bundle.py::validate_bundle`,
  `tests/test_operations_report_bundle.py`,
  `docs/operations-report-bundle-integrity-20260829.json`). Hosted SLO,
  preservation, elapsed and authority gates remain open.
- [x] R7 Require non-empty report identity and generation fields in the candidate bundle validator, with negative coverage (`scripts/build_operations_report_bundle.py`, `tests/test_operations_report_bundle.py`, `docs/operations-report-bundle-identity-validation-20260829.json`).

- [x] R5 Validate bounded coverage reports against their content digest, source-count shape and non-promotable national-coverage boundary (`src/riopa_provenance/archive_operations.py`, `tests/test_archive_operations.py`, `docs/operations-coverage-report-integrity-20260829.json`). Hosted national observations and release gates remain open.

- [x] R1 Constrain lifecycle transition endpoints to the declared job states and add a negative validation. Evidence: `schemas/operations-control.schema.json`, `tests/test_operations_control_contract.py`. (3af81f0)
- [x] R2 Record a bounded four-lens agent-panel qualification of operations, preservation and campaign controls without closing provider, elapsed, participant or authority gates (`docs/operations-panel-qualification-20260825.json`, `tests/test_operations_panel_qualification.py`).
- [x] R3 Reject malformed replication manifests, non-object receipts and duplicate target receipts before acceptance validation (`scripts/build_redundancy_manifest.py`, `tests/test_redundancy_manifest.py`).
- [x] R4 Bind the hosted recovery/rollback lane to the deterministic snapshot, restore and rollback harness rather than publication-only tests; retain production-representative recovery as an external gate (`scripts/record_hosted_evidence.py`, `tests/test_hosted_evidence.py`, `docs/operations-recovery-lane-contract-20260829.json`; 2026-08-29).
- [x] R8 Make beta/RC qualification activation explicit: supplemental drills remain retained without a cumulative elapsed ledger, while qualifying observations require an authority, activation timestamp and exact campaign binding (`.github/workflows/evidence-campaign.yml`, `scripts/record_hosted_evidence.py`, `schemas/hosted-evidence.schema.json`, `tests/test_hosted_evidence.py`, `docs/campaign-qualification-activation-20260829.json`; elapsed and promotion gates remain open).

## Track closeout

- [x] C.1 Link implementation, test, review, migration and release evidence in `index.md` for the repository-owned slice; hosted, preservation and elapsed gates remain explicitly pending.
- [x] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [x] C.4 Update metadata status and target-release evidence through the Conductor workflow; status remains `active`/M1 because the documented gates are unresolved.
