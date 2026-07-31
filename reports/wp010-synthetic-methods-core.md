# WP-010 synthetic simulation and causal-methods core

Date: 2026-07-31

## Implemented boundary

`schemas/analysis-protocol.schema.json` and
`src/riopa_provenance/analysis.py` define:

- an explicit estimand with population, exposure, comparison, outcome, time
  horizon and identification assumptions;
- parameter provenance classified as assumed, fitted or external, with evidence
  required for fitted and external values;
- master-seed, replication, warm-up, interval and convergence semantics;
- a deterministic FCFS capacity simulation and reproducible derived random
  streams for stochastic replications;
- a synthetic difference-in-differences calculation with pretrend and negative
  control diagnostics; and
- a pilot result envelope that marks clinical, legal, commercial and live
  operational suitability false.

## Verification

`tests/test_analysis.py` validates the schema projection, fail-closed protocol
rules, deterministic event ordering and queue metrics, seed reproducibility,
uncertainty with one and multiple replications, diagnostic hooks, invalid
inputs, and the non-operational interpretation boundary.

On 2026-07-31, 12 focused tests and the complete 248-test repository suite
passed together with Ruff, strict MyPy and diff checks.

## Claims and limitations

All inputs are synthetic. The reference queue is not an ambulance dispatch,
hospital capacity or supermarket model. The difference-in-differences function
calculates a contrast and exposes diagnostics; it does not establish parallel
trends, absence of interference, valid measurement, external validity or causal
identification. No empirical calibration, holdout validation, operational
review, public-data pilot or independent reproduction is claimed.
