# Plan: v1_release_hardening_20260719

## 1. Feature freeze and normative inventory

- [x] 1.1 Freeze v1 scope and inventory every public API, schema, ontology, CLI and file format. The repository-wide normative surface inventory is recorded and executable-validated; compatibility diffs remain task 1.2. (`docs/v1-normative-surface-inventory-20260825.json`, `tests/test_v1_release_readiness.py`)
- [x] 1.2 Generate compatibility diffs and resolve unintended breaking changes. The frozen predecessor at `409cbc7` has no removed public surface or changed schema constraint in the current inventory; additive surfaces and enum values are recorded in `docs/v1-compatibility-diff-20260825.json` and validated by `scripts/build_v1_compatibility_diff.py` and `tests/test_v1_compatibility_diff.py`.
- [x] 1.3 Formally defer or exclude non-v1 features and record explicit reopen criteria. The bounded regional public-datasets-only technical-preview boundary, disabled network/timetable/facility/national/clinical/dispatch surfaces and stable-promotion blocker are recorded in `docs/v1-non-v1-feature-disposition-20260825.json` and validated by `tests/test_v1_feature_disposition.py`.

## 2. Audit and rehearsal

- [~] 2.1 Complete the repository-owned security, performance, accessibility, governance and documentation audit slice. The machine-readable audit matrix is complete for bounded technical-preview evidence; external participant, elapsed, national-scale, preservation and accountable-authority gates remain open (`docs/v1-repository-audit-matrix-20260825.json`, `tests/test_v1_audit_matrix.py`).
- [ ] 2.2 Rehearse upgrade, migration, rollback, restore, correction and withdrawal.
- [ ] 2.3 Resolve P0/P1 defects and approve bounded P2 exceptions.

## 3. Release candidate validation

- [ ] 3.1 Build, sign, attest and preserve the exact release candidate.
- [ ] 3.2 Complete two clean-room reproductions and agent-operated user journeys.
- [ ] 3.3 Operate the candidate under stable SLOs and record incidents/deviations.

## 4. General availability and handover

- [ ] 4.1 Approve all machine-readable v1 release gates and governance decisions.
- [ ] 4.2 Publish stable artifacts, DOI/citations, support, deprecation and maintenance plan.
- [ ] 4.3 Announce v1.0, monitor adoption and begin the 1.x maintenance process.

## Track closeout

## 5. Review fixes

- [x] 5.1 Record a machine-readable, fail-closed v1 readiness baseline and explicit release blockers. (v1-release-readiness-baseline-20260801.json)
- [x] 5.2 Correct the readiness baseline boundary so it does not overstate completion of the normative inventory. (review fix)
- [x] 5.3 Record the capability/boundary map for hosted recovery, soak, scale, external workflows and release authority. (review fix)
- [x] 5.4 Adopt the single-developer agent-panel policy and record a fail-closed GitHub/Hugging Face remaining-gates plan with library options and contingencies. (review fix)
- [x] 5.5 Reconcile all normative review language to agent-panel qualification, stage daily hosted observations and record the GitHub/Hugging Face campaign-v2 plan. (review fix)
- [x] 5.6 Synchronise the validated issue graph to GitHub and record exact-head hosted check evidence. (`docs/github-issue-sync-20260802.json`)
- [x] 5.7 Protect `main` with strict hosted checks and no second-person review requirement. (`docs/github-main-protection-20260802.json`)
- [x] 5.8 Complete content-bound three-lens reports and an orchestrator synthesis for all 28 tracks without promoting any M6 disposition. (`docs/panel-reports/20260802/manifest.json`)
- [x] 5.9 Add portable workflow-lint and tracked-secret gates to local and hosted quality checks, with deterministic negative tests. (`scripts/check_workflow_lint.py`, `scripts/check_tracked_secrets.py`, `tests/test_ci_quality_gates.py`)
- [x] 5.10 Add a bounded, scheduled mutation lane with a pinned tool, explicit scope, threshold, raw-result artifact and score receipt. (`.github/workflows/mutation.yml`, `scripts/check_mutation_score.py`)
- [x] 5.11 Emit and retain a hosted receipt proving parity between the Python reference and Node standard-library conformance runner for the bounded corpus. (`scripts/verify_conformance_parity.py`, `.github/workflows/validate.yml`)
- [x] 5.12 Canonicalise solo-maintainer/security/contribution context and add a one-command context drift check. (`docs/solo-maintainer-security-context.md`, `scripts/validate_repo_context.py`)
- [x] 5.13 Close the quality-frontier parent issue with a dated, fail-closed scope record after subissues #145 and #146 were completed. (`docs/quality-frontier-closeout-20260821.json`)

- [ ] C.1 Link implementation, test, review, migration and release evidence in `index.md`.
- [ ] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [ ] C.4 Update metadata status and target-release evidence through the Conductor workflow.
