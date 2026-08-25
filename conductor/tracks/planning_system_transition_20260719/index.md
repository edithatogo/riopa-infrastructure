# Evidence index: Planning-system transition and legal continuity

- **Track ID:** `planning_system_transition_20260719`
- **Status:** `active`
- **Target release:** `0.7.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Reference`
- **Risk / priority:** `Critical` / `P1`
- **V1 critical:** `yes`
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Spatial data lead
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/84

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| PT-1 | Transition schema and fail-closed validator | `schemas/planning-transition.schema.json`, `src/riopa_provenance/transitions.py`, `tests/test_transitions.py` | Repository tests passing; real-data evidence not claimed |
| PT-2 | Rename, merge, split, replacement and partial-continuity fixtures | `fixtures/planning-transition-golden.json` | Deterministic fixture validated; not a legal equivalence claim |
| PT-3 | Temporal perspectives and migration guidance | `docs/planning-system-transition-migration-playbook.md` | Valid-time, recorded-time and as-known-at semantics documented |
| `PLANNING-TRANSITION-EVIDENCE-CROSSWALK-20260825` | Explicit discovery timing and confidence/scope-bounded continuity crosswalk contract | `src/riopa_provenance/transitions.py`, `tests/test_transitions.py`, `docs/planning-transition-evidence-crosswalk-contract-20260825.json` | Repository contract passes; real public-source history, legal authority, panel qualification and immutable release gates remain open |
| PT-4 | Downstream zoning and accessibility transition integration | `tests/test_transition_downstream.py`, `docs/planning-transition-downstream-contract.md` | Successor plan is selected at explicit valid time and passed to the dependency-free reference accessibility measure; synthetic only, with network/timetable/facility and legal claims disabled |
| `PLANNING-RECONSTRUCTION-SYNTHETIC-20260825` | One authority reorganisation and one plan replacement are represented as validated reconstruction cases | `fixtures/planning-transition-reconstruction.json`, `tests/test_planning_transition_reconstruction.py` | Synthetic reference cases validate; real historical evidence, legal authority and panel qualification remain open |
| `PLANNING-TRANSITION-PANEL-20260825` | Four-lens planning-transition contract qualification | `docs/planning-transition-panel-qualification-20260825.json`, `tests/test_planning_transition_panel_qualification.py` | Repository-owned bounded contract qualified; real-source, preservation, reproduction and authority gates remain open |

The same revision’s Conductor regeneration receipt records the methods hash,
roadmap status, generated issue graph and full quality harness. This closes only
the bookkeeping task; transition authority, operational, external and elapsed-
time gates remain open (`docs/planning-transition-conductor-regeneration-20260825.json`).

## Blocking defects

- Real authority reorganisation and plan replacement reconstructions remain
  pending; public-source capture, preservation and real-data reproduction are
  required before validation. The planning-domain agent-panel qualification is
  complete only for the repository-owned bounded contract. The downstream
  integration slice is bounded synthetic evidence, not real-data or operational
  qualification.

## Decisions, exceptions and limitations

- The repository-owned contract, fixtures and four-lens panel packet are complete
  for the current slice. Historical authority/plan reconstruction, immutable
  public-source evidence, real-data reproduction and release authority are still
  blocking validation. The downstream integration evidence is bounded synthetic
  coverage and does not satisfy the real-data gate.

## Review and handover

Required agent-panel lenses: Governance analyst, API/schema analyst, Data-governance analyst, Scientific-methods analyst.

## Review record

- Review scope: transition contract, fixtures, temporal selector, migration
  guidance, downstream integration and Conductor records through 2026-08-22.
- Finding: the playbook task cited the implementation commit rather than the
  commit that recorded the completed task, and pending gates were not mirrored
  in metadata.
- Fix: corrected the evidence reference and recorded the blockers explicitly.
- Additional fix: aligned the decisions register with PT-4 while retaining the
  real-data and external qualification boundaries.
- Current review: the new panel packet and test passed focused tests, roadmap
  validation and the full quality harness; the formatter correction is recorded
  as review fix `68807d4`. No external authority, preservation or real-data gate
  was inferred.

This index records the repository-owned implementation slice while the track remains `active`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, agent-panel qualified where required, and sufficient for the applicable release gates.
