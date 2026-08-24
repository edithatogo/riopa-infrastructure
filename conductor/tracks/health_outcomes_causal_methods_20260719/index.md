# Evidence index: Health-outcomes, spatial epidemiology and causal-methods framework

- **Track ID:** `health_outcomes_causal_methods_20260719`
- **Status:** `specified`
- **Target release:** `0.8.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Reference`
- **Risk / priority:** `Critical` / `P1`
- **V1 critical:** `yes`
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Research lead
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/104

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| `WP-010-analysis-protocol-and-did-reference-20260731` | Estimand, assumptions, parameter provenance and diagnostic hooks are machine-readable and causal claims remain bounded | `schemas/analysis-protocol.schema.json`, `src/riopa_provenance/analysis.py`, `tests/test_analysis.py`, `reports/wp010-synthetic-methods-core.md` | Synthetic DID contrast and diagnostics pass; empirical design, spatial sensitivity, preregistration and methods agent-panel qualification remain open |
| `WP-010-independent-fixture-calculation-20260801` | The committed synthetic estimand and expected DID contrast are recomputed by a standard-library verifier | `examples/wp010-synthetic-benchmark/`, `tests/test_wp010_benchmark.py` | Cross-implementation fixture passes locally; this does not establish causal identification or external reproduction |
| `HEALTH-ANALYSIS-DESIGN-SYNTHETIC-20260825` | Analysis type, DAG, estimand, population, exposure, comparator and outcome are explicit in a fail-closed schema | `schemas/health-analysis-design.schema.json`, `fixtures/health-analysis-design-synthetic.json`, `tests/test_health_analysis_design.py` | Synthetic non-clinical reference validates; empirical, clinical, spatial-sensitivity and panel gates remain open |

## Blocking defects

- Empirical/public-data design, spatial confounding and MAUP sensitivity,
  missing-data workflow, preregistration and methods agent-panel qualification remain
  open.

## Decisions, exceptions and limitations

- Diagnostics can reveal concerns but do not prove identification assumptions or
  support a causal conclusion.

## Review and handover

Required agent-panel lenses: Governance analyst, Data-governance analyst, Quantitative methods analyst, Scientific-methods analyst.

This index is deliberately non-assertive while the track remains `specified`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, agent-panel qualified where required, and sufficient for the applicable release gates.
