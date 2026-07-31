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
| `WP-010-public-source-intake-20260801` | Hospital and ambulance source candidates retain explicit provenance, rights and acquisition state | `config/source-registry/wp010-public-pilot-candidates.yaml`, `tests/test_wp010_benchmark.py` | LINZ hospital-facility metadata is staged; an authoritative national ambulance-station source remains unresolved and no operational use is claimed |

## Blocking defects

- An authoritative rights-cleared ambulance-station source, ambulance and hospital scenarios, dispatch/handover/relocation behaviour,
  calibrated stress tests and operational/safety review remain open.

## Decisions, exceptions and limitations

- The generic queue fixture cannot be used as an emergency-service or clinical
  decision system.

## Review and handover

Required reviewer roles: Governance reviewer, Research-object reviewer, Quantitative methods reviewer, Scientific reviewer.

This index is deliberately non-assertive while the track remains `specified`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, independently reviewed where required, and sufficient for the applicable release gates.
