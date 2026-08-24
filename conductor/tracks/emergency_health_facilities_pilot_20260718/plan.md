# Plan: emergency_health_facilities_pilot_20260718

## 1. Public benchmark design

- [x] 1.1 Define public/synthetic ambulance and hospital/service scenarios and a non-deployment statement. (`docs/emergency-health-pilot-benchmark-contract-20260825.json`; `498ee49`)
- [x] 1.2 Specify demand, fleet, staff, station, facility, travel, capacity and handover assumptions as synthetic or candidate-only inputs. (`docs/emergency-health-pilot-benchmark-contract-20260825.json`; `498ee49`)
- [x] 1.3 Define efficiency, tail, equity, rurality, resilience and cost metrics without clinical or dispatch interpretation. (`docs/emergency-health-pilot-benchmark-contract-20260825.json`, `tests/test_emergency_health_benchmark_contract.py`; `498ee49`)

## 2. Ambulance optimisation and simulation

- [ ] 2.1 Implement coverage, backup, availability and location scenarios.
- [ ] 2.2 Implement dispatch, queueing, handover and dynamic-relocation simulation.
- [ ] 2.3 Compare static and simulated performance under stress.

## 3. Hospital and service planning

- [ ] 3.1 Implement multi-service location, capacity, referral and workforce scenarios.
- [ ] 3.2 Add minimum volume, resilience, transition and phased investment constraints.
- [ ] 3.3 Report Pareto alternatives and non-modelled clinical constraints.

## 4. Safety and publication review

- [ ] 4.1 Conduct operational/safety, methods, governance and reproducibility review.
- [ ] 4.2 Resolve or bound all deployment-risk findings.
- [ ] 4.3 Publish benchmark research objects and explicit non-operational limitations.

## 5. Bounded WP-010 evidence

- [x] 5.1 Register hospital candidates and record the unresolved authoritative ambulance-source boundary. (bdb3af6)
- [x] 5.2 Capture separate council and OSM regional ambulance observations without national or operational claims. (37510dd)

## Track closeout

- [ ] C.1 Link implementation, test, review, migration and release evidence in `index.md`.
- [ ] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [ ] C.4 Update metadata status and target-release evidence through the Conductor workflow.
