# Plan: facility_location_engine_20260718

## 1. Problem and solution contracts

- [ ] 1.1 Define demand, candidates, travel, capacity, eligibility, cost and scenario schemas.
- [ ] 1.2 Define solver evidence, bounds, feasibility, uncertainty and explanation outputs.
- [ ] 1.3 Implement independent feasibility/objective verifier.

## 2. Core model families

- [ ] 2.1 Implement set covering, maximal covering, p-median and p-center.
- [ ] 2.2 Implement capacity, budget, fixed-site and eligibility constraints.
- [ ] 2.3 Add benchmark and intentionally corrupted solution suites.

## 3. Equity, robustness and extensions

- [ ] 3.1 Implement subgroup, max-min, inequality and Pareto alternatives.
- [ ] 3.2 Add scenario robustness/stochastic and multi-period interfaces.
- [ ] 3.3 Add competitive/market-capture reference formulation.

## 4. Scale and stable API

- [ ] 4.1 Benchmark representative national workloads and alternative solvers.
- [ ] 4.2 Integrate planning feasibility and accessibility inputs.
- [ ] 4.3 Freeze v1 API, model registry and migration policy.

## Track closeout

- [ ] C.1 Link implementation, test, review, migration and release evidence in `index.md`.
- [ ] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [ ] C.4 Update metadata status and target-release evidence through the Conductor workflow.
