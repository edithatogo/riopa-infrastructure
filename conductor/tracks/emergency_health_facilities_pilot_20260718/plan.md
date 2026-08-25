# Plan: emergency_health_facilities_pilot_20260718

## 1. Public benchmark design

- [x] 1.1 Define public/synthetic ambulance and hospital/service scenarios and a non-deployment statement. (`docs/emergency-health-pilot-benchmark-contract-20260825.json`; `498ee49`)
- [x] 1.2 Specify demand, fleet, staff, station, facility, travel, capacity and handover assumptions as synthetic or candidate-only inputs. (`docs/emergency-health-pilot-benchmark-contract-20260825.json`; `498ee49`)
- [x] 1.3 Define efficiency, tail, equity, rurality, resilience and cost metrics without clinical or dispatch interpretation. (`docs/emergency-health-pilot-benchmark-contract-20260825.json`, `tests/test_emergency_health_benchmark_contract.py`; `498ee49`)

## 2. Ambulance optimisation and simulation

- [x] 2.1 Implement coverage, backup, availability and location scenarios. Evidence: `CoverageScenario` and `evaluate_coverage_scenario` in `src/riopa_provenance/analysis.py` with synthetic primary/backup/availability tests; dispatch, clinical, operational and national claims remain disabled.
- [x] 2.2 Implement dispatch, queueing, handover and dynamic-relocation simulation. Evidence: `DispatchRequest`, `DispatchScenario`, `evaluate_dispatch_scenario` and `simulate_dispatch_scenario` provide deterministic synthetic adapters; live dispatch, clinical, operational and authority gates remain open.
- [x] 2.3 Compare static and simulated performance under a named synthetic stress profile. The bounded comparison reports assignment deltas, queue counts, maximum wait and changed assignments; calibrated, hosted, national-scale and operational-safety evidence remain open (`src/riopa_provenance/analysis.py:compare_static_simulated_stress`, `docs/emergency-health-stress-comparison-contract-20260825.json`, `tests/test_analysis.py`).

## 3. Hospital and service planning

- [x] 3.1 Implement a bounded synthetic multi-service location, capacity, referral and workforce scenario evaluator. Deterministic residual allocation and unmet-demand reporting are covered; real service data, clinical interpretation and operational qualification remain open (`src/riopa_provenance/analysis.py:ServiceScenario`, `src/riopa_provenance/analysis.py:evaluate_service_scenario`, `docs/emergency-health-services-contract-20260825.json`, `tests/test_analysis.py`).
- [x] 3.2 Add bounded synthetic minimum-volume, residual-resilience, transition-cost and phased-investment constraint checks. The checker reports constraint status without selecting an operational plan; real service data, clinical interpretation and operational qualification remain open (`src/riopa_provenance/analysis.py:evaluate_service_constraints`, `docs/emergency-health-constraints-contract-20260825.json`, `tests/test_analysis.py`).
- [x] 3.3 Report deterministic Pareto alternatives and explicitly non-modelled clinical/community constraints for caller-supplied synthetic candidates. The report is descriptive and promotion-disabled; real alternatives, safety review and operational interpretation remain open (`src/riopa_provenance/analysis.py:build_service_pareto_report`, `docs/emergency-health-pareto-contract-20260825.json`, `tests/test_analysis.py`).

## 4. Safety and publication review

- [x] 4.1 Conduct the repository-owned four-lens operational-safety, methods, governance and reproducibility panel review. The bounded packet qualifies repository contracts while leaving clinical, external, hosted, preservation and authority gates open (`docs/emergency-health-panel-qualification-20260825.json`, `tests/test_emergency_health_panel_qualification.py`).
- [x] 4.2 Resolve or bound deployment-risk findings. The packet records explicit non-operational boundaries and unresolved safety findings; it does not approve deployment (`docs/emergency-health-panel-qualification-20260825.json`).
- [x] 4.3 Prepare an unpublished benchmark research-object candidate and explicit non-operational limitations. Publication and preservation acceptance remain open (`docs/emergency-health-research-object-candidate-20260825.json`, `tests/test_emergency_health_panel_qualification.py`).

## 5. Bounded WP-010 evidence

- [x] 5.1 Register hospital candidates and record the unresolved authoritative ambulance-source boundary. (bdb3af6)
- [x] 5.2 Capture separate council and OSM regional ambulance observations without national or operational claims. (37510dd)

## Track closeout

- [x] C.1 Link implementation, test, review, migration, bounded stress-comparison and release evidence in `index.md` for the repository-owned closeout slice; stress, safety, authoritative-source, external and authority gates remain explicitly pending (`docs/emergency-health-closeout-evidence-20260825.json`, `docs/emergency-health-stress-comparison-contract-20260825.json`, `tests/test_emergency_health_closeout_evidence.py`; `1f84f9c`).
- [x] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected. The locked methods generation, roadmap status, issue graph and full quality harness passed; the methods output was temporary and not a release artifact (`docs/emergency-health-conductor-regeneration-20260825.json`).
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [ ] C.4 Update metadata status and target-release evidence through the Conductor workflow.

## Review fixes

- [x] R1 Wrap the benchmark-contract test path so the repository quality gate passes (`8c5c308`).
