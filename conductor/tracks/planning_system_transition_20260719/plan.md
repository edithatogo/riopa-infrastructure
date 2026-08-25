# Plan: planning_system_transition_20260719

## 1. Transition model

- [x] 1.1 Define legislation, authority, instrument and provision transition relationships. (transition schema; implementation)
- [x] 1.2 Define legal/status and knowledge-time assertions and uncertainty. (transitions.py; implementation)
- [x] 1.3 Add transition fixtures for rename, merge, split, replacement and partial continuity. (planning-transition-golden.json; implementation)

## 2. Historical reconstruction

- [x] 2.1 Reconstruct one authority reorganisation and one plan replacement. (`fixtures/planning-transition-reconstruction.json`, `tests/test_planning_transition_reconstruction.py`; synthetic reference only)
- [~] 2.2 Preserve contemporaneous and retrospectively discovered evidence separately through explicit discovery-mode validation; real historical records remain open (`src/riopa_provenance/transitions.py`, `tests/test_transitions.py`).
- [~] 2.3 Build continuity crosswalks with confidence and scope. Bounded fail-closed crosswalk construction is implemented; real authority histories and immutable public-source evidence remain open (`src/riopa_provenance/transitions.py`, `tests/test_transitions.py`, `docs/planning-transition-evidence-crosswalk-contract-20260825.json`).

## 3. Temporal query integration

- [x] 3.1 Add valid-time, recorded-time and as-known-at query modes. (transitions.py; implementation)
- [x] 3.2 Test downstream zoning and accessibility analyses across transitions. (`a3ef9ae`; bounded synthetic reference contract)
- [x] 3.3 Document non-equivalence and unresolved transitions. (planning-system-transition-migration-playbook.md)

## 4. Agent-panel qualification and migration readiness

- [x] 4.1 Conduct planning-domain agent-panel qualification and resolve model findings. The four-lens repository-owned packet qualifies the bounded transition contract and records unresolved real-source, preservation, reproduction and authority gates (`docs/planning-transition-panel-qualification-20260825.json`, `tests/test_planning_transition_panel_qualification.py`; `e8ab512`).
- [x] 4.2 Publish future-reform migration playbook. (planning-system-transition-migration-playbook.md; 11ead57; recorded 2f544c2)
- [ ] 4.3 Release transition data and limitations with immutable evidence.

## 5. Review fixes

- [x] 5.1 Correct the migration-playbook evidence SHA and record pending reconstruction/review gates explicitly. (review fix)
- [x] 5.2 Align the decisions register with the completed bounded downstream integration evidence and retain only the real-data, panel and immutable-source blockers. (review fix; 2026-08-22)
- [x] 5.3 Apply the repository formatter to the new panel qualification test after review (`68807d4`).

## Track closeout

- [ ] C.1 Link implementation, test, review, migration and release evidence in `index.md`.
- [x] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected. The locked methods generation, roadmap status, issue graph and full quality harness passed; the methods output was temporary and not a release artifact (`docs/planning-transition-conductor-regeneration-20260825.json`).
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [ ] C.4 Update metadata status and target-release evidence through the Conductor workflow.
