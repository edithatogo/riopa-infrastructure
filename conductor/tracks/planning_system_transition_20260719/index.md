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

## Blocking defects

- Real authority reorganisation and plan replacement reconstructions remain pending; public-source capture and domain review are required before validation.

## Decisions, exceptions and limitations

- None recorded.

## Review and handover

Required reviewer roles: Governance reviewer, API/schema reviewer, Data steward, Scientific reviewer.

This index records the repository-owned implementation slice while the track remains `active`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, independently reviewed where required, and sufficient for the applicable release gates.
