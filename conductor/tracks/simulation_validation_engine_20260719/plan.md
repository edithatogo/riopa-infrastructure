# Plan: simulation_validation_engine_20260719

## 1. Simulation contract and RNG

- [x] 1.1 Define event, resource, queue, demand, service and policy contracts. (`src/riopa_provenance/analysis.py`, `schemas/analysis-protocol.schema.json`)
- [x] 1.2 Define random stream, seed, replication, warm-up and convergence semantics. (`src/riopa_provenance/analysis.py`, `tests/test_analysis.py`)
- [x] 1.3 Build deterministic toy and stochastic reference fixtures. (`examples/wp010-synthetic-benchmark/`, `tests/test_analysis.py`)

## 2. Reference simulation engine

- [x] 2.1 Implement the bounded generic discrete-event FCFS execution and metrics reference. (`src/riopa_provenance/analysis.py::simulate_fcfs_queue`, `tests/test_analysis.py`; dispatch, clinical/service adapters and operational qualification remain open.)
- [x] 2.2 Add dispatch, backup coverage, dynamic relocation and handover adapters. Evidence: `DispatchScenario` and `evaluate_dispatch_scenario` in `src/riopa_provenance/analysis.py` with deterministic synthetic tests; live dispatch, clinical, operational and authority gates remain open.
- [x] 2.3 Add a bounded synthetic service-capacity resilience example. (`src/riopa_provenance/capacity_models.py::evaluate_capacity_resilience`, `tests/test_capacity_models.py`; no hospital, clinical, dispatch, national-scale or operational claim is made.)

## 3. Calibration and validation

- [~] 3.1 Define fitted, assumed and externally sourced parameter evidence. `parameter_evidence_report` preserves each declared source class and required references; no empirical or source-authority claim is made (`src/riopa_provenance/analysis.py`, `tests/test_analysis.py`).
- [~] 3.2 Add calibration, holdout validation and sensitivity workflows. Synthetic caller-supplied calibration and seeded candidate-grid sensitivity are implemented; real-data holdout and external validation remain open (`src/riopa_provenance/analysis.py`, `tests/test_analysis.py`, `docs/simulation-calibration-sensitivity-contract-20260825.json`).
- [ ] 3.3 Compare independent implementation or published benchmark behaviour.

## 4. Integration and stable release

- [ ] 4.1 Stress-test facility-location solutions under stochastic scenarios.
- [ ] 4.2 Validate controlled/public data boundaries and performance.
- [ ] 4.3 Freeze the v1 simulation and result contracts.

## 5. Bounded WP-010 evidence

- [x] 5.1 Package a dependency-free deterministic queue benchmark for independent handoff. (bdb3af6)

## Track closeout

- [x] C.1 Link implementation, test, review, migration and release evidence in `index.md`; the bounded synthetic contract and FCFS evidence are linked.
- [x] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [x] C.4 Update metadata status and target-release evidence through the Conductor workflow; status remains active/M1 because domain, calibration, independent and operational gates are unresolved.
