# Plan: planning_system_transition_20260719

## 1. Transition model

- [x] 1.1 Define legislation, authority, instrument and provision transition relationships. (transition schema; implementation)
- [x] 1.2 Define legal/status and knowledge-time assertions and uncertainty. (transitions.py; implementation)
- [x] 1.3 Add transition fixtures for rename, merge, split, replacement and partial continuity. (planning-transition-golden.json; implementation)

## 2. Historical reconstruction

- [ ] 2.1 Reconstruct one authority reorganisation and one plan replacement.
- [ ] 2.2 Preserve contemporaneous and retrospectively discovered evidence separately.
- [ ] 2.3 Build continuity crosswalks with confidence and scope.

## 3. Temporal query integration

- [x] 3.1 Add valid-time, recorded-time and as-known-at query modes. (transitions.py; implementation)
- [ ] 3.2 Test downstream zoning and accessibility analyses across transitions.
- [x] 3.3 Document non-equivalence and unresolved transitions. (planning-system-transition-migration-playbook.md)

## 4. Agent-panel qualification and migration readiness

- [ ] 4.1 Conduct planning-domain agent-panel qualification and resolve model findings.
- [x] 4.2 Publish future-reform migration playbook. (planning-system-transition-migration-playbook.md; 11ead57; recorded 2f544c2)
- [ ] 4.3 Release transition data and limitations with immutable evidence.

## 5. Review fixes

- [x] 5.1 Correct the migration-playbook evidence SHA and record pending reconstruction/review gates explicitly. (review fix)

## Track closeout

- [ ] C.1 Link implementation, test, review, migration and release evidence in `index.md`.
- [ ] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [ ] C.4 Update metadata status and target-release evidence through the Conductor workflow.
