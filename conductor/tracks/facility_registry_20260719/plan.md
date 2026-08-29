# Plan: facility_registry_20260719

The current implementation slice is active and evidence-gated. Public food-retail
packets are archived and reconciled only as source assertions. This plan does not
promote a source to authoritative status without a documented panel disposition.

## 0 Runtime and evidence policy

- [x] 0.1 Restrict packaging, linting, typing and hosted CI to Python 3.14 only (`pyproject.toml`, workflow files and `scripts/verify_github_main_protection.py`).
- [x] 0.2 Preserve immutable source packets and record their hosted revisions, payload hashes and limitations in the evidence index.
- [x] 0.3 Build a deterministic bounded review frame; panel disposition remains an evidence gate. (`scripts/build_facility_review_sample.py`, `docs/facility-stratified-review-sample-20260803.json`)

## 1. Facility/source model

- [x] 1.1 Define facility assertion identities in the bounded reference contract; operator, service and stable registry identities remain release work.
- [x] 1.2 Define source coordinates, optional uncertainty, rights, authority and observation fields for bounded source assertions; temporal registry state remains release work.
- [x] 1.3 Register rights-cleared public supermarket and health-service source families; three public food-retail families and two distinct public health families are archived. Reconciliation, currentness and authority remain release gates.

## 2. Acquisition and reconciliation

- [x] 2.1 Archive independent public council and OSM assertions with immutable receipts before reconciliation; verified health and broader geocoded evidence remain open.
- [x] 2.2 Implement deterministic type/name/distance candidate generation and conflict preservation; accountable adjudication remains open.
- [x] 2.3 Record openings, closures, relocations and rebrands. (`412c252`; append-only history events and deterministic snapshot)

## 3. Quality and review

- [x] 3.1 Build a deterministic stratified duplicate, classification and coordinate review sample; panel disposition remains pending. (`scripts/build_facility_review_sample.py`, `docs/facility-stratified-review-sample-20260803.json`)
- [x] 3.2 Record bounded source sensitivity; performance estimates require a reference sample qualified by the agent panel.
- [x] 3.3 Implement sensitive/restricted release filtering. (`ad87365`; public-only projection with exclusion ledger)

## 4. Stable registry release

- [x] 4.1 Integrate registry versions with accessibility and planning queries. Public-only, non-authoritative assertions supply accessibility opportunity weights and bounded planning candidates; the accessibility matrix binding requires an explicit public registry version and fails closed on stale/private destinations. Planning authority, canonical registry identity, real-network integration and operational availability remain pending (`src/riopa_provenance/facility_location.py:candidates_from_public_facility_snapshot`, `src/riopa_provenance/accessibility.py::bind_public_facility_registry`, `docs/facility-public-planning-adapter-contract-20260825.json`, `docs/facility-accessibility-binding-20260825.json`).
- [x] 4.2 Generate bounded source disagreement and coverage reports over
  archived assertions. (`disagreement_coverage_report`, tests)
- [x] 4.3 Release immutable registry snapshot and correction process. Content-addressed public-only snapshot records require an explicit registry version and validate optional predecessor digests as an unpublished repository-owned candidate; publication and accountable release approval remain pending (`src/riopa_provenance/facility_registry.py`, `docs/facility-snapshot-version-contract-20260825.json`, `tests/test_facility_registry.py`).

## Track closeout

- [x] C.1 Link implementation, test, review, migration and release evidence in `index.md` for the bounded public projection; panel and authority gates remain explicitly pending.
- [x] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [x] C.4 Update metadata status and target-release evidence through the Conductor workflow; status remains `active`/M1 because the documented gates are unresolved.

## Review fixes

- [x] 5.1 Enforce the history event-type union at runtime, add a negative test,
  and align the evidence-index lifecycle wording with active metadata. (review fix; 2026-08-22)
- [x] 5.2 Verify the public-only release projection, preserve the exclusion
  ledger and align the history evidence row after task 3.3. (review fix; 2026-08-22)
- [x] 5.3 Align the G.1 lifecycle marker with the completed agent-panel frame
  qualification while retaining factual adjudication as an open gate. (review fix; 2026-08-29)
- [x] 5.4 Validate historical stable-gate snapshots by their self-contained
  digest rather than recomputing them against mutable current metadata. (review fix; 2026-08-29)

## Evidence gates still open

- [x] G.1 Agent-panel qualification of the deterministic 741-row review frame is recorded in `docs/facility-panel-frame-qualification-20260825.json`; factual pair/sample adjudication remains open and no promotion is enabled.
- [x] G.2 Record the Hamilton packet as explicitly attribute-only because all 3,245 archived assertions have null geometry (`docs/facility-panel-qualification-20260803.json`, `docs/facility-food-reconciliation-20260803.json`, `tests/test_public_dataset_archive_plan.py`). No geometry, completeness or authoritative facility claim is enabled.
- [x] G.3 A second public health source family with an immutable archive receipt. The bounded Rangitīkei public ambulance-facility assertions are registered from the preserved Zenodo successor packet with a verified payload digest (`config/archive-sources/rangitikei-public-ambulance-2023.json`, `docs/public-health-ambulance-source-qualification-20260825.json`, `tests/test_public_dataset_archive_plan.py`). Reconciliation, currentness, completeness, authoritative ambulance coverage and operational use remain disabled.
- [x] G.4 Stable public-only, non-authoritative registry projection with source-disagreement and coverage reports is implemented and tested (`FACILITY-DISAGREEMENT-COVERAGE-20260822`, `FACILITY-SNAPSHOT-CORRECTION-20260824`). Completeness, panel adjudication, publication and accountable release approval remain open.
- [ ] G.5 Immutable release snapshot, correction process and accountable release-authority decision.

## Historical hosted merge-policy blocker (resolved 2026-08-03)

The code and required checks were green, but GitHub reported the protected PR as
`BLOCKED` after the main-branch check contract changed from Python 3.12/3.13 to
Python 3.14. PR #177 subsequently resolved this policy-state issue through an
owner-authorized administrative merge. The event is historical and is not a
current track blocker or release evidence.

Historical options and contingencies (retained for audit):

1. **Recommended:** create a fresh PR from the current clean branch so GitHub
   evaluates the current protection rules against a new pull request head.
2. **Fallback:** wait with auto-merge enabled if the fresh PR also remains
   blocked; record the unchanged policy response and escalate to repository
   administration/support.
3. **Last resort:** administrator merge, only with an explicit release-authority
   decision because it bypasses the protected merge gate.

- [x] G.6 Reconcile hosted merge policy through a fresh PR. PR #177 merged on
  2026-08-03 as an explicitly recorded administrative exception after all
  required checks passed; this is not release evidence.
- [x] G.7 Repair the stale PR #175 blocker wording after confirming the merge-policy
  resolution and preserve the superseded blocker only as historical context.
  (`index.md`, review fix 2026-08-25)
