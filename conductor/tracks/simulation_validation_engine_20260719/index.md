# Evidence index: Stochastic service simulation and model validation engine

- **Track ID:** `simulation_validation_engine_20260719`
- **Status:** `active`
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
| `WP-010-synthetic-simulation-core-20260731` | Seeded replication, warm-up, uncertainty and convergence semantics are explicit and deterministic | `schemas/analysis-protocol.schema.json`, `src/riopa_provenance/analysis.py`, `tests/test_analysis.py`, `reports/wp010-synthetic-methods-core.md` | Synthetic queue reference passes; calibration, holdout, independent benchmark, domain adapters and agent-panel qualification remain open |
| `WP-010-clean-room-benchmark-20260801` | A dependency-free verifier independently recomputes fixed queue and causal-reference expectations | `examples/wp010-synthetic-benchmark/`, `scripts/build_wp010_reviewer_bundle.py`, `tests/test_wp010_benchmark.py` | Deterministic repository-owned handoff passes; agent-panel execution remains open |
| `SIMULATION-CONTRACT-20260822` | Event/queue protocol, seeded replication, warm-up/convergence semantics and deterministic fixtures | `src/riopa_provenance/analysis.py`, `schemas/analysis-protocol.schema.json`, `examples/wp010-synthetic-benchmark/`, `tests/test_analysis.py` | Repository-owned synthetic contract and fixtures pass; domain adapters, calibration, independent comparison and operational qualification remain open |
| `SIMULATION-DISPATCH-ADAPTER-20260825` | Synthetic dispatch, backup, relocation and handover adapter contract | `src/riopa_provenance/analysis.py:DispatchScenario`, `src/riopa_provenance/analysis.py:evaluate_dispatch_scenario`, `tests/test_analysis.py` | Deterministic contract passes; no live dispatch, clinical suitability, response guarantee or operational authority is claimed |
| `SIMULATION-FCFS-ENGINE-CLOSEOUT-20260825` | Bounded generic discrete-event FCFS engine emits ordered events, wait metrics and utilisation | `src/riopa_provenance/analysis.py::simulate_fcfs_queue`, `tests/test_analysis.py` | Bounded synthetic execution is tested; dispatch, hospital/service adapters, empirical calibration and operational claims remain disabled |
| `SIMULATION-CAPACITY-RESILIENCE-20260825` | Synthetic primary/backup capacity, unmet demand and reserve-gap calculation is deterministic and fail-closed | `src/riopa_provenance/capacity_models.py::evaluate_capacity_resilience`, `tests/test_capacity_models.py` | Bounded service-capacity example passes; no hospital, clinical, dispatch, national-scale or operational claim is made |
| `SIMULATION-CALIBRATION-SENSITIVITY-20260825` | Parameter source classification, synthetic candidate calibration and seeded sensitivity grid preserve assumptions and non-claims | `src/riopa_provenance/analysis.py`, `tests/test_analysis.py`, `docs/simulation-calibration-sensitivity-contract-20260825.json` | Synthetic caller-supplied workflow passes; real-data holdout, external validation, independent benchmark and operational qualification remain open |
| `SIMULATION-V1-REFERENCE-CONTRACT-20260825` | Bounded synthetic/reference simulation surfaces, compatibility rules and required evidence controls | `docs/simulation-v1-reference-contract-20260825.md`, `docs/simulation-v1-reference-contract-20260825.json`, `tests/test_simulation_v1_contract.py` | Contract freeze is repository-owned; empirical, independent, operational, national-scale and release gates remain open |
| `SIMULATION-STOCHASTIC-STRESS-20260825` | Seeded, caller-supplied stochastic stress rehearsal over a bounded facility-location reference fixture | `src/riopa_provenance/facility_location.py:stochastic_stress_test`, `docs/simulation-stochastic-stress-rehearsal-20260825.json`, `tests/test_simulation_stochastic_stress.py` | Four deterministic replications pass with promotion disabled; calibrated, hosted, national-scale and operational stress evidence remains open |
| `SIMULATION-BOUNDARY-PERFORMANCE-20260825` | Fail-closed public/synthetic/controlled input and observed performance-envelope validator | `src/riopa_provenance/capacity_models.py:validate_simulation_boundary`, `docs/simulation-boundary-performance-contract-20260825.json`, `tests/test_capacity_models.py` | Live inputs and silent extrapolation are rejected; source authority, hosted, national-scale, operational and release evidence remain open |

## Blocking defects

- Empirical calibration/validation, independent benchmark comparison and
  performance qualification remain open.

## Decisions, exceptions and limitations

- The FCFS queue is a synthetic contract fixture and is not an emergency,
  hospital or other operational simulation.

## Review and handover

Required agent-panel lenses: Provenance analyst, Operations analyst, Quantitative methods analyst, Scientific-methods analyst.

This index is deliberately non-assertive while the track remains `active` at M1. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, agent-panel qualified where required, and sufficient for the applicable release gates.
