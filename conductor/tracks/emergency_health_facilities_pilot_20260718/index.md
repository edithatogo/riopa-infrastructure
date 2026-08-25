# Evidence index: Ambulance and hospital facility-planning reference pilots

- **Track ID:** `emergency_health_facilities_pilot_20260718`
- **Status:** `active`
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
| `WP-010-regional-ambulance-observation-20260801` | Council and OSM regional observations remain separate by authority and licence | `scripts/capture_wp010_public_sources.py`, `tests/test_wp010_public_sources.py`, `reports/wp010-synthetic-methods-core.md` | Three council and two OSM ambulance POIs observed; no national completeness or dispatch suitability is claimed |
| `WP-010-COVERAGE-SCENARIO-20260825` | Synthetic primary/backup/availability/location scenario contract | `src/riopa_provenance/analysis.py:CoverageScenario`, `src/riopa_provenance/analysis.py:evaluate_coverage_scenario`, `tests/test_analysis.py` | Deterministic fixture passes; no dispatch, clinical suitability, response guarantee, national completeness or authority claim is made |
| `WP-010-DISPATCH-QUEUE-20260825` | Synthetic dispatch, queueing, handover and dynamic-relocation adapter contract | `src/riopa_provenance/analysis.py:DispatchRequest`, `src/riopa_provenance/analysis.py:simulate_dispatch_scenario`, `tests/test_analysis.py` | Deterministic queue fixture passes; no live dispatch, clinical, response, national or operational claim is made |
| `EMERGENCY-HEALTH-STRESS-COMPARISON-20260825` | Static-versus-simulated comparison under a named synthetic stress profile | `src/riopa_provenance/analysis.py:compare_static_simulated_stress`, `tests/test_analysis.py`, `docs/emergency-health-stress-comparison-contract-20260825.json` | Assignment deltas and queue waits are deterministic over synthetic inputs; calibrated, hosted, national-scale and operational-safety evidence remain open |
| `EMERGENCY-HEALTH-SERVICES-20260825` | Synthetic multi-service capacity, referral and workforce scenario | `src/riopa_provenance/analysis.py:ServiceScenario`, `src/riopa_provenance/analysis.py:evaluate_service_scenario`, `tests/test_analysis.py`, `docs/emergency-health-services-contract-20260825.json` | Residual capacity/workforce allocation and unmet demand are deterministic; real service, clinical, operational and authority evidence remain open |
| `EMERGENCY-HEALTH-CONSTRAINTS-20260825` | Synthetic minimum-volume, resilience, transition-cost and phased-investment constraint checks | `src/riopa_provenance/analysis.py:evaluate_service_constraints`, `tests/test_analysis.py`, `docs/emergency-health-constraints-contract-20260825.json` | Constraint status is deterministic and promotion-disabled; no operational plan, clinical recommendation or authority claim is made |
| `EMERGENCY-HEALTH-PARETO-20260825` | Synthetic Pareto frontier report with explicitly non-modelled clinical/community constraints | `src/riopa_provenance/analysis.py:build_service_pareto_report`, `tests/test_analysis.py`, `docs/emergency-health-pareto-contract-20260825.json` | Frontier is descriptive and promotion-disabled; real alternatives, safety review and operational interpretation remain open |
| `EMERGENCY-HEALTH-PANEL-20260825` | Four-lens repository-owned safety, methods, governance and reproducibility panel packet | `docs/emergency-health-panel-qualification-20260825.json`, `tests/test_emergency_health_panel_qualification.py` | Bounded repository evidence is assessed; clinical, external, hosted, preservation and authority gates remain open |
| `EMERGENCY-HEALTH-RESEARCH-OBJECT-20260825` | Unpublished benchmark research-object candidate with explicit non-operational limitations | `docs/emergency-health-research-object-candidate-20260825.json`, `tests/test_emergency_health_panel_qualification.py` | Candidate packet is promotion-disabled and not deposited or preserved |
| `EMERGENCY-HEALTH-BENCHMARK-CONTRACT-20260825` | Bounded public/synthetic ambulance and hospital planning scenarios, assumptions and non-clinical metrics | `docs/emergency-health-pilot-benchmark-contract-20260825.json`, `tests/test_emergency_health_benchmark_contract.py` | Contract is repository-owned and promotion-disabled; authoritative ambulance source, calibrated scenarios, clinical/dispatch safety and external qualification remain open |
| `EMERGENCY-HEALTH-CLOSEOUT-EVIDENCE-20260825` | Link implementation, tests, review, migration and release-candidate evidence for the bounded emergency-health slice | `docs/emergency-health-closeout-evidence-20260825.json`, `tests/test_emergency_health_closeout_evidence.py` | Evidence categories are linked and fail-closed; stress, safety, authoritative-source, external and authority gates remain open |
| `EMERGENCY-HEALTH-CONDUCTOR-REGENERATION-20260825` | Locked methods, roadmap status, issue graph and quality regeneration receipt | `docs/emergency-health-conductor-regeneration-20260825.json` | Repository generation passed; temporary methods output is not a release artifact and roadmap readiness remains false |

## Blocking defects

- A national authoritative ambulance-station source, ambulance and hospital scenarios, dispatch/handover/relocation behaviour,
  calibrated stress tests and operational/safety review remain open.

## Decisions, exceptions and limitations

- The generic queue fixture cannot be used as an emergency-service or clinical
  decision system.

The 2026-08-25 closeout packet links the bounded coverage, dispatch-simulation,
source-candidate and benchmark-contract evidence. It does not establish
calibrated stress performance, clinical or dispatch suitability, authoritative
source completeness, operational safety or a stable release.

The same revision’s Conductor regeneration receipt records the methods hash,
roadmap status, generated issue graph and full quality harness. This closes only
the bookkeeping task; it does not change the track’s maturity or external gates.

## Review and handover

Required agent-panel lenses: Governance analyst, Research-object analyst, Quantitative methods analyst, Scientific-methods analyst.

This index is deliberately non-assertive while the track remains `active` at M1. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, agent-panel qualified where required, and sufficient for the applicable release gates.
