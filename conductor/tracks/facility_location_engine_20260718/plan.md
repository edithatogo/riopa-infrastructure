# Plan: facility_location_engine_20260718

## 1. Problem and solution contracts

- [x] 1.1 Define demand, candidates, travel, capacity, eligibility, cost and scenario schemas. (`src/riopa_provenance/facility_location.py`, `tests/test_facility_location.py`)
- [x] 1.2 Define solver evidence, bounds, feasibility, uncertainty and explanation outputs. (`src/riopa_provenance/facility_location.py`, `tests/test_facility_location.py`)
- [x] 1.3 Implement independent feasibility/objective verifier. (`src/riopa_provenance/facility_location.py:verify_solution`, `tests/test_facility_location.py`)

## 2. Core model families

- [x] 2.1 Implement set covering, maximal covering, p-median and p-center. Bounded exhaustive reference models are implemented; national-scale solver qualification remains open. (`src/riopa_provenance/facility_location.py`, `tests/test_facility_location.py`)
- [x] 2.2 Implement capacity, budget, fixed-site and eligibility constraints. (`src/riopa_provenance/facility_location.py`, `tests/test_facility_location.py`)
- [x] 2.3 Add benchmark and intentionally corrupted solution suites. Bounded line benchmarks and negative verifier cases pass; trusted external benchmark references remain open. (`tests/test_facility_location.py`, `reports/wp009-reference-solver-cores.md`)

## 3. Equity, robustness and extensions

- [x] 3.1 Implement subgroup, minimax subgroup-mean and Pareto alternatives. The minimax selector is an explicit bounded equity alternative and does not silently replace the model objective. (`src/riopa_provenance/facility_location.py:minimax_subgroup_alternative`, `tests/test_facility_location.py`; commit `cb92f43`)
- [x] 3.2 Add scenario robustness/stochastic and multi-period interfaces. Evidence: deterministic `RobustScenario`, `evaluate_robust_scenarios` and `MultiPeriodPlan` reference interfaces with tests; no probability, forecast, operational or national claim is made.
- [x] 3.3 Add competitive/market-capture reference formulation. Evidence: `competitive_capture_reference` provides an explicit gravity-share sensitivity calculation with deterministic tests; it is not a market forecast or operational claim.

## 4. Scale and stable API

- [~] 4.1 Benchmark bounded reference workloads and alternative exhaustive models. The local harness records cardinality and environment-bound timing; national-scale workloads, external solvers and production qualification remain open (`src/riopa_provenance/facility_location.py`, `tests/test_facility_location.py`, `docs/facility-reference-benchmark-contract-20260825.json`).
- [~] 4.2 Integrate planning feasibility and accessibility inputs through a
  fail-closed bounded reference adapter. Archived accessibility observations,
  explicit candidate eligibility and optional impedance thresholds are applied
  without inferring authority or operations (`src/riopa_provenance/facility_location.py`,
  `docs/facility-location-bounded-input-adapter-20260825.md`,
  `docs/facility-location-bounded-input-adapter-contract-20260825.json`,
  `tests/test_facility_location.py`). National, live network/timetable,
  planning-authority and release evidence remain open.
- [~] 4.3 Freeze v1 API, model registry and migration policy. Supported bounded
  reference model names and compatibility/breaking-change rules are documented;
  national-scale, planning/accessibility, external-solver, operational and
  release gates remain open (`docs/facility-location-v1-api-migration-policy-20260825.md`,
  `docs/facility-location-v1-api-migration-contract-20260825.json`,
  `tests/test_facility_location_v1_policy.py`).

## Track closeout

- [x] C.1 Link implementation, test, review, migration and release evidence in `index.md` for the repository-owned closeout slice; scale, external benchmark, authority and release gates remain explicitly pending (`docs/facility-location-closeout-evidence-20260825.json`, `tests/test_facility_location_closeout_evidence.py`; `045831f`).
- [x] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected. The locked methods generation, roadmap status, issue graph and full quality harness passed; the methods output was temporary and not a release artifact (`docs/facility-location-conductor-regeneration-20260825.json`).
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [ ] C.4 Update metadata status and target-release evidence through the Conductor workflow.
