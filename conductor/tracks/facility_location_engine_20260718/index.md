# Evidence index: Inspectable facility-location and allocation engine

- **Track ID:** `facility_location_engine_20260718`
- **Status:** `specified`
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
| `WP-009-reference-location-core-20260731` | Four canonical model families, explicit capacity/fixed/eligibility/equity constraints, deterministic Pareto outputs and independent feasibility verification | `src/riopa_provenance/facility_location.py`, `tests/test_facility_location.py`, `reports/wp009-reference-solver-cores.md` | 35 combined core tests pass with 100% statement and branch coverage for both new modules; scalable external solvers and independent external benchmark review remain open |

## Blocking defects

- Scalable solver adapters, certificate interchange, national workloads and
  independent external benchmark verification remain open.

## Decisions, exceptions and limitations

- Exhaustive enumeration is intentionally bounded to small correctness fixtures
  and must not be represented as an operational planning engine.

## Review and handover

Required reviewer roles: API/schema reviewer, External user reviewer, Quantitative methods reviewer, Scientific reviewer.

This index is deliberately non-assertive while the track remains `specified`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, independently reviewed where required, and sufficient for the applicable release gates.
