# Plan: documentation_developer_experience_20260719

## 1. Information architecture and contract inventory

- [x] 1.1 Inventory audiences, workflows, interfaces and required references. (`docs/documentation-information-architecture-20260824.md`)
- [x] 1.2 Map documentation pages to normative sources and release versions. (`docs/documentation-information-architecture-20260824.md`, `docs/documentation-contract-20260824.json`)
- [x] 1.3 Define executable tutorial and example conventions. (`docs/tutorial-and-example-conventions-20260824.md`, `tests/test_documentation_contract.py`)

## 2. Documentation implementation

- [x] 2.4 Reconcile portable work-package implementation status separately from qualification, generate a read-only evidence-bound progress report, and provide tested archived Tasman query examples without new source acquisition (`f145368`; `docs/repository-progress-reporting-20260831.md`).

- [x] 2.1 Write user, operator, contributor, maintainer and migration guides. (`docs/usage-guides-20260825.md`, `tests/test_usage_guides.py`; bounded technical-preview handoff only)
- [x] 2.2 Generate API, CLI, schema and ontology references. (`docs/reference-index-20260825.json`, `tests/test_reference_index.py`; deterministic surface index, not external usability evidence)
- [x] 2.3 Build public/synthetic end-to-end tutorials and troubleshooting diagnostics. (`docs/bounded-lineage-tutorial-20260825.md`, `scripts/run_bounded_lineage_tutorial.py`, `tests/test_bounded_lineage_tutorial.py`; synthetic offline rehearsal only)

## 3. Independent usability validation

- [~] 3.1 Run owner-authorized agent user and operator workflow studies. A protected-main agent-user-workflows rehearsal passed at run `32739643452`; role-separated agent user/operator journey evidence remains mandatory.
- [x] 3.2 Run the repository-owned accessibility, terminology, safety and limitations review through a bounded agent-panel packet. The packet and deterministic checks are repository-owned evidence; other-human participant and accessibility validation remain open (`docs/documentation-inventory-and-safety-review-20260825.json`, `tests/test_documentation_inventory_review.py`).
- [x] 3.3 Document anticipated friction and support burden from bounded workflows. The historical register was not another-human user evidence; prospectively the required role-separated agent user/operator journeys are governed by the programme panel policy (`docs/documentation-friction-register-20260825.json`, `tests/test_documentation_friction_register.py`).

## 4. Stable support readiness

- [x] 4.1 Execute every tutorial against one immutable repository-candidate revision through the bounded rehearsal harness. This is not RC promotion evidence; agent-operated user/operator journey evidence, elapsed RC soak and accountable authority remain open. (`scripts/run_release_candidate_tutorials.py`, `tests/test_release_candidate_tutorials.py`; `16ff727`)
- [x] 4.2 Freeze the preview support channels, triage, single-developer ownership and sustainability bounds (`docs/documentation-support-readiness-20260825.json`, `tests/test_documentation_support_readiness.py`). Stable support, external participation, RC soak and authority gates remain open.
- [x] 4.3 Build a content-addressed versioned documentation archive candidate. The manifest is content-addressed, unpublished and explicitly not RC/stable evidence; external usability, preservation acceptance, publication and authority remain open (`scripts/build_documentation_archive_manifest.py`, `docs/documentation-archive-manifest-20260825.json`, `tests/test_documentation_archive_manifest.py`).

## Track closeout

- [x] C.1 Link implementation, test, review, migration and release evidence in `index.md` for the repository-owned closeout slice; external usability, preservation and release-authority gates remain explicitly pending (`docs/documentation-closeout-evidence-20260825.json`, `tests/test_documentation_closeout_evidence.py`; `c79bda0`).
- [x] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected. The locked methods generation, roadmap status, issue graph and full quality harness passed; the methods output was temporary and not a release artifact (`docs/documentation-conductor-regeneration-20260825.json`).

## Review fixes

- [x] R2 Bind current archive summary claims to parsed acceptance receipts, rejecting drift in publication status, immutable revisions, counts, rights and qualification boundaries (PR #763; `scripts/report_repository_progress.py`, `tests/test_repository_progress.py`; 43 tests and isolated cross-review passed).
- [x] R1 Add a fail-closed validator for the bounded owner-authorized agent workflow report, retaining the external-participant and promotion boundaries (`scripts/validate_agent_user_workflow_report.py`, `tests/test_agent_user_workflow_report_validator.py`, `docs/documentation-agent-workflow-report-validation-20260829.json`; 2026-08-29).
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [x] C.4 Update metadata status and target-release evidence through the Conductor workflow; metadata is `active`/M1 for target release `0.9.0`, with external usability, preservation, RC-soak and authority gates unresolved.

## Review fixes

- [x] R1 Wrap the long nonclaim string so the repository quality gate passes (`3d62c46`).
- [x] Synchronize GitHub phase issues #125–#128 from the generated projection and
  record exact body digests; no external usability, preservation, soak, promotion
  or authority gate is closed (`docs/documentation-issue-sync-20260830.json`).
- [x] Add a successor CLI-output receipt for the deployed issue bodies while
  preserving the original local-source receipt (`docs/documentation-issue-sync-20260830-receipt-v2.json`).
