# Evidence index: Stochastic service simulation and model validation engine

- **Track ID:** `simulation_validation_engine_20260719`
- **Status:** `specified`
- **Target release:** `0.8.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Platform`
- **Risk / priority:** `Critical` / `P1`
- **V1 critical:** `yes`
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Methods and analytics lead
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/94

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| `WP-010-synthetic-simulation-core-20260731` | Seeded replication, warm-up, uncertainty and convergence semantics are explicit and deterministic | `schemas/analysis-protocol.schema.json`, `src/riopa_provenance/analysis.py`, `tests/test_analysis.py`, `reports/wp010-synthetic-methods-core.md` | Synthetic queue reference passes; calibration, holdout, independent benchmark, domain adapters and external review remain open |

## Blocking defects

- Domain simulation adapters, empirical calibration/validation, independent
  benchmark comparison and performance qualification remain open.

## Decisions, exceptions and limitations

- The FCFS queue is a synthetic contract fixture and is not an emergency,
  hospital or other operational simulation.

## Review and handover

Required reviewer roles: Provenance reviewer, Operations reviewer, Quantitative methods reviewer, Scientific reviewer.

This index is deliberately non-assertive while the track remains `specified`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, independently reviewed where required, and sufficient for the applicable release gates.
