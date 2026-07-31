# Evidence index: Ambulance and hospital facility-planning reference pilots

- **Track ID:** `emergency_health_facilities_pilot_20260718`
- **Status:** `specified`
- **Target release:** `0.8.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Reference`
- **Risk / priority:** `Critical` / `P1`
- **V1 critical:** `yes`
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Research lead
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/99

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| `WP-010-non-operational-capacity-fixture-20260731` | Capacity simulation outputs carry an explicit non-operational suitability boundary | `src/riopa_provenance/analysis.py`, `tests/test_analysis.py`, `reports/wp010-synthetic-methods-core.md` | Synthetic FCFS fixture passes; no ambulance, hospital, clinical or dispatch suitability is claimed |

## Blocking defects

- Ambulance and hospital scenarios, dispatch/handover/relocation behaviour,
  calibrated stress tests and operational/safety review remain open.

## Decisions, exceptions and limitations

- The generic queue fixture cannot be used as an emergency-service or clinical
  decision system.

## Review and handover

Required reviewer roles: Governance reviewer, Research-object reviewer, Quantitative methods reviewer, Scientific reviewer.

This index is deliberately non-assertive while the track remains `specified`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, independently reviewed where required, and sufficient for the applicable release gates.
