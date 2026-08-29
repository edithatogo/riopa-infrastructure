# Plan: v1_release_hardening_20260719

## 1. Feature freeze and normative inventory

- [x] 1.1 Freeze v1 scope and inventory every public API, schema, ontology, CLI and file format. The repository-wide normative surface inventory is recorded and executable-validated; compatibility diffs remain task 1.2. (`docs/v1-normative-surface-inventory-20260825.json`, `tests/test_v1_release_readiness.py`)
- [x] 1.2 Generate compatibility diffs and resolve unintended breaking changes. The frozen predecessor at `409cbc7` has no removed public surface or changed schema constraint in the current inventory; additive surfaces and enum values are recorded in `docs/v1-compatibility-diff-20260825.json` and validated by `scripts/build_v1_compatibility_diff.py` and `tests/test_v1_compatibility_diff.py`.
- [x] 1.3 Formally defer or exclude non-v1 features and record explicit reopen criteria. The bounded regional public-datasets-only technical-preview boundary, disabled network/timetable/facility/national/clinical/dispatch surfaces and stable-promotion blocker are recorded in `docs/v1-non-v1-feature-disposition-20260825.json` and validated by `tests/test_v1_feature_disposition.py`.

## 2. Audit and rehearsal

- [x] 2.1 Complete the repository-owned security, performance, accessibility, governance and documentation audit slice. The machine-readable audit matrix is complete for bounded technical-preview evidence; other-human participant, elapsed, national-scale, preservation and accountable-authority gates remain open (`docs/v1-repository-audit-matrix-20260825.json`, `tests/test_v1_audit_matrix.py`).
- [x] 2.2 Rehearse upgrade, migration, rollback, restore, correction and withdrawal through the bounded repository matrix. Contract and hosted technical-preview drill evidence is linked; production-representative restore, independent target acceptance, downstream notification and release-authority gates remain open (`docs/v1-upgrade-rehearsal-matrix-20260825.json`, `tests/test_v1_upgrade_rehearsal_matrix.py`).
- [x] 2.3 Reconcile P0/P1 defect dispositions and record that no bounded P2 exceptions are approved. P0/P1 external, elapsed and scope gates remain open in `docs/v1-defect-disposition-20260825.json`, validated by `tests/test_v1_defect_disposition.py`; no defect is silently waived.

## 3. Release candidate validation

- [x] 3.1 Prepare the exact release-candidate packet and protected signing sequence. The fail-closed packet binds the current protected-main revision and lists signing, attestation, preservation, participant, soak and authority gates; protected signing and accepted preservation remain external (`docs/v1-release-candidate-packet-20260825.json`, `tests/test_v1_release_candidate_packet.py`).
- [x] 3.2 Record two distinct owner-authorized agent-operated journeys against repository-bound workflows. The journeys are repository-owned rehearsal evidence; two qualifying clean-room reproductions and role-separated agent operator/user journey evidence remain open (`docs/v1-agent-operated-journeys-20260825.json`, `tests/test_v1_agent_operated_journeys.py`).
- [x] 3.2a Add a deterministic exact-candidate continuity evaluator. It identifies three individually valid RC observations across three candidate revisions and therefore records a required reset without combining their duration (`scripts/build_v1_release_gate_snapshot.py`, `docs/v1-stable-release-gate-snapshot-20260825.json`, `tests/test_v1_release_gate_snapshot.py`).
- [x] 3.2b Execute the bounded clean-room rehearsal and agent-user journey lanes against the exact frozen candidate `26bc0b4`. Both hosted runs pass, but their receipts explicitly do not constitute isolated multi-agent clean-room reproduction or agent-operated user/operator journey evidence (`docs/v1-candidate-hosted-validation-20260825.json`; runs `32856533103` and `32856537212`).
- [ ] 3.3 Operate the candidate under stable SLOs and record incidents/deviations.
- [x] 3.3a Start a fresh isolated exact-candidate RC segment at `26bc0b4`. The first schema-validated hosted observation passes with one candidate revision and one 11-second observation; the 30-day duration gate remains pending (`docs/v1-candidate-hosted-validation-20260825.json`; run `32856370956`).
- [x] 3.3b Start a fresh isolated beta operational segment at `26bc0b4`. Its first schema-validated hosted observation passes with one candidate revision, one second and one operational cycle; the 90-day and three-cycle gates remain pending (`docs/v1-candidate-hosted-validation-20260825.json`; run `32857084789`).
- [x] 3.3c Pin the daily hosted operational schedule to the isolated beta campaign, qualification epoch and immutable `26bc0b4` candidate so later `main` changes do not reset its accumulating segment (`.github/workflows/evidence-campaign.yml`, `tests/test_campaign_v2.py`).
- [x] 3.3d Verify the merged workflow defaults without supplying campaign, epoch or candidate inputs. The cumulative ledger advances to two observations over 428 seconds at one candidate and epoch; the actual scheduled event remains pending (`docs/v1-candidate-hosted-validation-20260825.json`; run `32857832666`).

## 4. General availability and handover

- [ ] 4.1 Approve all machine-readable v1 release gates and governance decisions.
- [x] 4.1a Reconcile current track, stable-gate, campaign, release-evidence and authority state into a non-authorizing machine-readable snapshot. The result is blocked and permits no promotion (`docs/v1-stable-release-gate-snapshot-20260825.json`).
- [x] 4.1b Refresh the non-authorizing gate snapshot against protected-main revision `898c5c2` while preserving the historical snapshot; the successor remains blocked at 0/28 tracks and 0/14 gates (`docs/v1-stable-release-gate-snapshot-20260829.json`).
- [x] 4.1c Refresh the non-authorizing snapshot from the exact clean merged reconciliation revision `40ef0515`; `v0.4.0` preview preservation is reconciled while stable v1 remains blocked at 0/28 tracks and 0/14 gates (`docs/v1-stable-release-gate-snapshot-20260829-40ef0515.json`, `tests/test_v1_release_gate_snapshot.py`).
- [ ] 4.2 Publish stable artifacts, DOI/citations, support, deprecation and maintenance plan.
- [ ] 4.3 Announce v1.0, monitor adoption and begin the 1.x maintenance process.

## Track closeout

## 5. Review fixes

- [x] 5.1 Record a machine-readable, fail-closed v1 readiness baseline and explicit release blockers. (v1-release-readiness-baseline-20260801.json)
- [x] 5.2 Correct the readiness baseline boundary so it does not overstate completion of the normative inventory. (review fix)
- [x] 5.3 Record the capability/boundary map for hosted recovery, soak, scale, agent-operated workflows and release authority. (review fix)
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
- [x] 5.14 Require the two agent-journey packet references to resolve to existing workflows and evidence documents, preventing stale journey claims.
- [x] 5.15 Refresh the Python 3.14 module and branch-aware coverage inventory after the bounded accessibility, planning, replication and journey slices (`docs/module-coverage-inventory-20260825.json`).
- [x] 5.16 Harden the stable-gate snapshot review findings: validate revision and UTC timestamp syntax, include evidence and dependency maturity in track qualification, expose continuity failure reasons and verify the content digest. (`7553a18`, `0411449`)
- [x] 5.17 Correct the stale multi-candidate reset claim after starting the isolated `26bc0b4` RC campaign; retain explicit duration, external-evidence, preservation and authority boundaries. (`80bf631`)
- [x] 5.18 Correct the moving-main beta schedule so daily observations remain bound to the isolated campaign, qualification epoch and immutable candidate; clarify the shared beta/RC dispatch input. (`bf84ef6`)
- [x] 5.19 Assemble the exact-revision `0.3.0` experimental M2 release-evidence
  record, close its four repository-owned core gates without waivers, and retain
  every `0.4.0` through stable-v1 blocker. (`conductor/release-evidence/0.3.0.json`,
  `tests/test_v030_release_evidence.py`)
- [x] 5.20 Normalize the release-hardening metadata timestamp to UTC without
  changing the v0.3 evidence decision or any later release boundary. (Conductor
  review fix)
- [x] 5.21 Coordinate the package, citation, CodeMeta, programme and release-note
  surfaces for the protected `v0.3.0` tag, with an executable version-drift and
  later-release-boundary test. (`tests/test_v030_release_preparation.py`)
- [x] 5.22 Make the protected publisher mark experimental `v0.*` and explicit
  prerelease tags as GitHub prereleases without affecting future stable tags.
  (`.github/workflows/release.yml`, `tests/test_v030_release_preparation.py`;
  Conductor review fix)
- [x] 5.23 Publish the exact `v0.3.0` workflow artifacts after checksum,
  attestation and tag verification; record the automated publication failure,
  bounded manual recovery and asset digests without claiming a fully passed
  release workflow. (`docs/v0.3.0-release-publication-20260827.json`)
- [x] 5.24 Add the missing tagged-source checkout to the protected publish job so
  future `--verify-tag` publication runs have Git context. (`.github/workflows/release.yml`;
  review fix)
- [x] 5.25 Add a revision-bound stable-v1 readiness plan with all 14 gate families,
  beta/RC clock-reset rules, preservation fallback and explicit non-substitutions;
  keep the record preparation-only and promotion fail-closed. (`docs/stable-v1-readiness-plan-20260829.json`,
  `docs/stable-v1-readiness-plan-20260829.md`, `tests/test_stable_v1_readiness_plan.py`)

- [x] C.1 Link implementation, test, review, migration and release evidence in `index.md` for the bounded candidate packet; external, elapsed, preservation and authority gates remain open (`docs/v1-release-closeout-evidence-20260825.json`, `tests/test_v1_release_closeout_evidence.py`).
- [x] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected. The locked methods generation, roadmap status, issue graph and full quality harness passed; the methods output was temporary and not a release artifact (`docs/v1-release-conductor-regeneration-20260825.json`).
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [x] C.4 Update metadata status and target-release evidence through the Conductor workflow; metadata remains `active`/M1 for target release `1.0.0`, with elapsed soak, agent-operated workflows, preservation, performance, isolated multi-agent clean-room reproduction and accountable-authority gates unresolved.
