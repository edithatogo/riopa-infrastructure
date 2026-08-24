# Plan: facility_registry_20260719

The current implementation slice is active and evidence-gated. Public food-retail
packets are archived and reconciled only as source assertions. This plan does not
promote a source to authoritative status without a documented panel disposition.

## 0 Runtime and evidence policy

- [x] 0.1 Restrict packaging, linting, typing and hosted CI to Python 3.14 only (`pyproject.toml`, workflow files and `scripts/verify_github_main_protection.py`).
- [x] 0.2 Preserve immutable source packets and record their hosted revisions, payload hashes and limitations in the evidence index.
- [~] 0.3 Build a deterministic bounded review frame; panel disposition remains an evidence gate.

## 1. Facility/source model

- [x] 1.1 Define facility assertion identities in the bounded reference contract; operator, service and stable registry identities remain release work.
- [x] 1.2 Define source coordinates, optional uncertainty, rights, authority and observation fields for bounded source assertions; temporal registry state remains release work.
- [~] 1.3 Register rights-cleared public supermarket and health-service source families; three public food-retail families are archived, while a second public health family remains open.

## 2. Acquisition and reconciliation

- [x] 2.1 Archive independent public council and OSM assertions with immutable receipts before reconciliation; verified health and broader geocoded evidence remain open.
- [x] 2.2 Implement deterministic type/name/distance candidate generation and conflict preservation; accountable adjudication remains open.
- [x] 2.3 Record openings, closures, relocations and rebrands. (`412c252`; append-only history events and deterministic snapshot)

## 3. Quality and review

- [~] 3.1 Build a deterministic stratified duplicate, classification and coordinate review sample; panel disposition is pending.
- [x] 3.2 Record bounded source sensitivity; performance estimates require a reference sample qualified by the agent panel.
- [x] 3.3 Implement sensitive/restricted release filtering. (`ad87365`; public-only projection with exclusion ledger)

## 4. Stable registry release

- [~] 4.1 Integrate registry versions with accessibility and planning queries. A public-only, non-authoritative assertion projection now supplies unit opportunity weights to accessibility measures; planning integration and authoritative registry identity remain pending.
- [x] 4.2 Generate bounded source disagreement and coverage reports over
  archived assertions. (`disagreement_coverage_report`, tests)
- [~] 4.3 Release immutable registry snapshot and correction process. A content-addressed public-only snapshot record and append-successor validator are implemented; publication and accountable release approval remain pending.

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

## Evidence gates still open

- [ ] G.1 Agent-panel disposition of the 39 candidate pairs and the deterministic review sample.
- [ ] G.2 Geometry-bearing or explicitly attribute-only disposition for the Hamilton packet.
- [ ] G.3 A second public health source family with an immutable archive receipt.
- [ ] G.4 Stable registry projection, source-disagreement and coverage reports.
- [ ] G.5 Immutable release snapshot, correction process and accountable release-authority decision.

## Hosted merge-policy blocker (2026-08-03)

The code and required checks are green, but GitHub reports the protected PR as
`BLOCKED` after the main-branch check contract changed from Python 3.12/3.13 to
Python 3.14. This is an external policy-state gate, not an implementation defect.

Options and contingencies:

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
