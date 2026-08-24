# Evidence index: Inspectable facility-location and allocation engine

- **Track ID:** `facility_location_engine_20260718`
- **Status:** `active`
- **Target release:** `0.7.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Platform`
- **Risk / priority:** `Critical` / `P1`
- **V1 critical:** `yes`
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Methods and analytics lead
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/79

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| `WP-009-reference-location-core-20260731` | Four canonical model families, explicit capacity/fixed/eligibility/equity constraints, deterministic Pareto outputs and independent feasibility verification | `src/riopa_provenance/facility_location.py`, `tests/test_facility_location.py`, `reports/wp009-reference-solver-cores.md` | 35 combined core tests pass with 100% statement and branch coverage for both new modules; scalable external solvers and agent-panel benchmark qualification remain open |
| `FACILITY-LOCATION-CONTRACT-RECONCILIATION-20260824` | Conductor phases 1–2 are reconciled to the existing bounded reference implementation and negative-test evidence | `conductor/tracks/facility_location_engine_20260718/plan.md`, `src/riopa_provenance/facility_location.py`, `tests/test_facility_location.py`, `reports/wp009-reference-solver-cores.md` | Bounded contracts, four model families, constraints, verifier and corruption tests are complete; equity/robustness extensions, national scale, external benchmark and release gates remain open |
| `FACILITY-LOCATION-EQUITY-ALTERNATIVE-20260824` | Explicit minimax subgroup-mean selector is available as a bounded equity alternative | `src/riopa_provenance/facility_location.py:minimax_subgroup_alternative`, `tests/test_facility_location.py` | Selector is deterministic and independently verifiable; it does not establish policy preference, national-scale performance or operational authority |
| `FACILITY-LOCATION-COMPETITIVE-20260825` | Explicit gravity-share sensitivity formulation for selected candidates | `src/riopa_provenance/facility_location.py:competitive_capture_reference`, `tests/test_facility_location.py` | Deterministic bounded shares pass; no market forecast, commercial, national-scale or operational claim is made |
| `FACILITY-LOCATION-ROBUSTNESS-20260825` | Deterministic perturbation and multi-period reference interfaces | `src/riopa_provenance/facility_location.py:RobustScenario`, `src/riopa_provenance/facility_location.py:MultiPeriodPlan`, `tests/test_facility_location.py` | Bounded scenario and period contracts pass; probability, forecasting, national-scale, operational and external solver evidence remain open |

## Blocking defects

- Scalable solver adapters, certificate interchange, national workloads and
  independent external benchmark verification remain open.

## Decisions, exceptions and limitations

- Exhaustive enumeration is intentionally bounded to small correctness fixtures
  and must not be represented as an operational planning engine.

## Review and handover

Required agent-panel lenses: API/schema analyst, External-user workflow analyst, Quantitative methods analyst, Scientific-methods analyst.

This index is deliberately non-assertive while the track remains `active`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, agent-panel qualified where required, and sufficient for the applicable release gates.
