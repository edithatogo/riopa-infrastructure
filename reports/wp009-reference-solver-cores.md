# WP-009 reference accessibility and facility-location cores

Date: 2026-07-31

## Implemented boundary

Accessibility measurement and facility optimisation are separate reusable
modules:

- `src/riopa_provenance/accessibility.py` defines a versioned, mode-specific
  travel matrix with distinct reachable, unreachable, missing and censored
  observations. It implements cumulative opportunity, exponential gravity and
  unweighted two-step floating catchment measures.
- `src/riopa_provenance/facility_location.py` defines inspectable small-instance
  contracts and exhaustive reference solvers for set covering, maximal
  covering, p-median and p-center. Capacity, fixed-site, eligibility,
  opening-cost, budget and subgroup mean-distance constraints are explicit.

The solver returns status, objective, bound, gap and tolerance fields. A
separate verifier recalculates structural feasibility, capacity, coverage,
equity, subgroup summaries and objective values from the public problem
contract. Malformed or intentionally corrupted solutions fail closed with
specific errors.

## Verification

`tests/test_accessibility.py` and `tests/test_facility_location.py` contain
hand-calculated line instances, capacity/fixed/eligibility examples, explicit
equity constraints, deterministic Pareto comparisons, invalid contracts and
corrupted-solution checks.

Focused verification on 2026-07-31:

- 35 tests passed;
- both new modules achieved 100% statement and branch coverage;
- Ruff formatting/checks and strict MyPy passed;
- the complete repository test, quality and reproducibility gates passed.

## Claims and limitations

These are transparent exhaustive reference implementations for small benchmark
instances. They are suitable as correctness oracles and contract fixtures, not
national-scale solvers. They do not implement road/timetable engines, opening
hours, stochastic optimisation, multi-period planning, solver-independent
certificate formats or national performance benchmarks. No output is an
operational, clinical, planning, investment or commercial recommendation.
