# Evidence index: Multimodal accessibility and travel-matrix engine

- **Track ID:** `accessibility_network_engine_20260719`
- **Status:** `specified`
- **Target release:** `0.6.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Platform`
- **Risk / priority:** `High` / `P1`
- **V1 critical:** `yes`
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Methods and analytics lead
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/54

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| `WP-009-reference-accessibility-core-20260731` | Versioned travel observations preserve missing/unreachable/censored semantics and hand-calculated accessibility measures | `src/riopa_provenance/accessibility.py`, `tests/test_accessibility.py`, `reports/wp009-reference-solver-cores.md` | Bounded dependency-free reference core passes; multimodal adapters, real NZ integration, scale and external review remain open |

## Blocking defects

- Real road, walk, cycle and timetable engines; national-scale benchmarking; and
  scientific/user review remain open.

## Decisions, exceptions and limitations

- The reference matrix and measures are correctness fixtures, not a claim of
  national routing coverage or operational service accessibility.

## Review and handover

Required reviewer roles: API/schema reviewer, Data steward, Quantitative methods reviewer, Scientific reviewer.

This index is deliberately non-assertive while the track remains `specified`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, independently reviewed where required, and sufficient for the applicable release gates.
