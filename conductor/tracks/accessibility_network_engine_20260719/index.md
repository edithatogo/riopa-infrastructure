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
| `WP-009-reference-accessibility-core-20260731` | Versioned travel observations preserve missing/unreachable/censored semantics and hand-calculated accessibility measures | `src/riopa_provenance/accessibility.py`, `tests/test_accessibility.py`, `reports/wp009-reference-solver-cores.md` | Bounded dependency-free reference core passes; multimodal adapters, real NZ integration, scale and agent-panel qualification remain open |
| `ACCESS-ARCHIVED-INPUTS-20260802` | Real accessibility inputs are acquired as independent immutable network, timetable, demand and facility archives | `docs/public-dataset-archive-incorporation-plan-20260802.json`, [open_social_data issue 35](https://github.com/edithatogo/open_social_data/issues/35), [open_social_data issue 37](https://github.com/edithatogo/open_social_data/issues/37) | Source routes defined; archived feeds, cross-engine benchmarks and national measurements remain pending |
| `ACCESS-MESHBLOCK-SUPPORT-20260802` | Exact national supporting-geography bytes are available without treating geography as demand, destinations or routing evidence | [Hugging Face packet revision](https://huggingface.co/datasets/edithatogo/riopa-public-data-archive/tree/3f2dc0a4d95a4fcb495551098d58fc5bce9c9202), `docs/public-dataset-archive-incorporation-plan-20260802.json` | Full Meshblock 2026 archive verified; population, network, timetable, destination and accessibility measurements remain open |
| `ACCESS-CONTRACT-V1-20260822` | Versioned travel-matrix and reference-only measure contracts with explicit missing/unreachable/censored semantics | `schemas/accessibility-matrix.schema.json`, `schemas/accessibility-measure.schema.json`, `docs/accessibility-contract-v1.md`, `tests/test_accessibility.py` | Contract tests pass; real network/timetable archives, national measurements and operational claims remain disabled |
| `ACCESS-SCENARIO-CONTRACT-20260824` | Explicit reference-only uncertainty, subgroup and scenario contract | `schemas/accessibility-scenario.schema.json`, `src/riopa_provenance/accessibility.py:validate_scenario_contract`, `tests/test_accessibility.py` | Assumptions, subgroup uniqueness and missing-data semantics are validated; real network, timetable and operational qualification remain open |

## Blocking defects

- Real road, walk, cycle and timetable engines; national-scale benchmarking; and
  scientific-methods/user-workflow agent-panel qualification remains open.

## Decisions, exceptions and limitations

- The reference matrix and measures are correctness fixtures, not a claim of
  national routing coverage or operational service accessibility.

## Review and handover

Required agent-panel lenses: API/schema analyst, Data-governance analyst, Quantitative methods analyst, Scientific-methods analyst.

This index is deliberately non-assertive while the track remains `specified`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, agent-panel qualified where required, and sufficient for the applicable release gates.
