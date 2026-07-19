# Plan: simulation_validation_engine_20260719

## 1. Simulation contract and RNG

- [ ] 1.1 Define event, resource, queue, demand, service and policy contracts.
- [ ] 1.2 Define random stream, seed, replication, warm-up and convergence semantics.
- [ ] 1.3 Build deterministic toy and stochastic reference fixtures.

## 2. Reference simulation engine

- [ ] 2.1 Implement generic discrete-event execution and metrics.
- [ ] 2.2 Add dispatch, backup coverage, dynamic relocation and handover adapters.
- [ ] 2.3 Add hospital/service capacity and resilience examples.

## 3. Calibration and validation

- [ ] 3.1 Define fitted, assumed and externally sourced parameter evidence.
- [ ] 3.2 Add calibration, holdout validation and sensitivity workflows.
- [ ] 3.3 Compare independent implementation or published benchmark behaviour.

## 4. Integration and stable release

- [ ] 4.1 Stress-test facility-location solutions under stochastic scenarios.
- [ ] 4.2 Validate controlled/public data boundaries and performance.
- [ ] 4.3 Freeze the v1 simulation and result contracts.

## Track closeout

- [ ] C.1 Link implementation, test, review, migration and release evidence in `index.md`.
- [ ] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [ ] C.4 Update metadata status and target-release evidence through the Conductor workflow.
