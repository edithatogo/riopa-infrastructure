# Track: Stochastic service simulation and model validation engine

Track ID: `simulation_validation_engine_20260719`  
Phase: **Analytics**  
Target release: **0.8.0**  
Maturity target: **M6**  
Stability class: **Platform**  
V1 critical: **yes**

## Goal

Provide reproducible discrete-event and dispatch simulation for systems where availability, queueing, congestion, handover or dynamic relocation invalidate static location models.

## v1 role

This track is part of the stable v1 release contract. It is complete only when its implementation, compatibility, quality, security/governance, operational and reproducibility evidence satisfy both this specification and every applicable blocking gate in `conductor/releases.json` and `conductor/v1-gate.json`.

## Dependencies


- `canonical_domain_schemas_ontology_20260719`
- `facility_location_engine_20260718`

## Scope

- Generic events, resources, demand processes, service times, routing, queues and policies.
- Seed management, replications, warm-up, variance, calibration and validation.
- Ambulance dispatch, busy fraction, backup coverage, handover and dynamic relocation adapters.
- Hospital/service capacity, referral, failure and resilience scenarios.
- Static-optimisation comparison, uncertainty, sensitivity and performance.

## Out of scope

- Deploying simulation recommendations into live operations.
- Representing sensitive operational data in public fixtures.

## Requirements

- **R01.** Stochastic inputs and empirical/calibrated assumptions are versioned separately.
- **R02.** Seeds and replication design permit statistical reproduction without claiming byte identity.
- **R03.** Simulation validity is assessed against withheld or benchmark behaviour where possible.
- **R04.** Static and simulated objectives are compared using common scenario identifiers.
- **R05.** Operationally sensitive adapters support controlled data without leaking it to public releases.

## Acceptance criteria

- [ ] A generic simulation contract supports arrivals, queues, resources, dispatch, service, transport and outcome events.
- [ ] Replication, warm-up, confidence interval, seed and convergence diagnostics are automated.
- [ ] Public benchmark models cover busy/backup ambulance coverage and capacity/queueing behaviour.
- [ ] Calibration/validation evidence distinguishes fitted, assumed and externally sourced parameters.
- [ ] Static location solutions can be stress-tested under stochastic unavailability and congestion.
- [ ] Results are reproducible statistically and pass independent implementation or benchmark comparison.

## Hardening and maturity gates

- M2 requires executable proof, negative tests and traceable evidence; interfaces may remain experimental.
- M3 requires real-data integration, migration evidence and representative failure handling.
- M4 requires repeated operation, external use, SLO evidence and bounded compatibility changes.
- M5 requires frozen interfaces, orchestrated agent-panel qualification, security/performance/recovery qualification and release-candidate soak.
- M6 requires supported compatibility, signed and preserved releases, external reproduction, named maintainers and post-release verification.
- Exceptions must be machine-readable, scoped, approved, time-limited and visible in release evidence.

## Evidence required

- Simulation event and parameter specifications.
- Seed/replication/convergence and validation reports.
- Public ambulance and hospital/service benchmark models.
- Static-versus-simulation stress-test results.

## Risks

- A detailed simulator creates false realism from weak assumptions.
- Calibration overfits one period or region.
- Parallel random streams are not reproducible.
- Sensitive operational patterns are disclosed through examples.

## Completion rule

The track may enter `complete` only after every acceptance criterion is evidenced in `index.md`, all blocking dependencies are complete, required migrations and documentation are published, and the target release readiness evaluator reports no track-specific blocker.
