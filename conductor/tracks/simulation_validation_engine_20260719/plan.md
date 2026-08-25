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

- [x] 3.1 Define fitted, assumed and externally sourced parameter evidence. `parameter_evidence_report` preserves each declared source class and required references; no empirical or source-authority claim is made (`src/riopa_provenance/analysis.py`, `tests/test_analysis.py`).
- [x] 3.2 Add calibration, holdout validation and sensitivity workflows. Synthetic caller-supplied calibration and seeded candidate-grid sensitivity are implemented; real-data holdout and external validation remain open (`src/riopa_provenance/analysis.py`, `tests/test_analysis.py`, `docs/simulation-calibration-sensitivity-contract-20260825.json`).
- [x] 3.3 Compare the FCFS engine with a separate availability-list reference path (`src/riopa_provenance/analysis.py::compare_fcfs_reference_implementations`, `docs/simulation-reference-crosscheck-20260825.json`, `tests/test_analysis.py`). This is an internal bounded cross-check; external implementation, published benchmark, real-data and operational validation remain open.

## 4. Integration and stable release

- [x] 4.1 Stress-test facility-location solutions under stochastic scenarios. A seeded, caller-supplied perturbation rehearsal now covers bounded reference fixtures; calibrated, hosted, national-scale and operational stress evidence remains open (`docs/simulation-stochastic-stress-rehearsal-20260825.json`, `tests/test_simulation_stochastic_stress.py`).
- [x] 4.2 Validate controlled/public data boundaries and performance. A fail-closed validator now rejects live inputs, requires rights/governance references and blocks performance extrapolation beyond observed envelopes; hosted, national-scale and operational evidence remains open (`src/riopa_provenance/capacity_models.py:validate_simulation_boundary`, `docs/simulation-boundary-performance-contract-20260825.json`).
- [x] 4.3 Freeze the bounded v1 simulation and result contracts. Supported
  synthetic/reference surfaces, compatibility rules and required seed,
  parameter-evidence, uncertainty and missingness controls are documented;
  empirical, independent, operational, national-scale and release gates remain
  open (`docs/simulation-v1-reference-contract-20260825.md`,
  `docs/simulation-v1-reference-contract-20260825.json`,
  `tests/test_simulation_v1_contract.py`).

## 5. Bounded WP-010 evidence

- [x] 5.1 Package a dependency-free deterministic queue benchmark for independent handoff. (bdb3af6)

## Track closeout

- [x] C.1 Link implementation, test, review, migration and release evidence in `index.md`; the bounded synthetic contract and FCFS evidence are linked.
- [x] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [x] C.4 Update metadata status and target-release evidence through the Conductor workflow; status remains active/M1 because domain, calibration, independent and operational gates are unresolved.
