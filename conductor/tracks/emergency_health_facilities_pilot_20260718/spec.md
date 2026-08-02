# Track: Ambulance and hospital facility-planning reference pilots

Track ID: `emergency_health_facilities_pilot_20260718`  
Phase: **Applications**  
Target release: **0.8.0**  
Maturity target: **M6**  
Stability class: **Reference**  
V1 critical: **yes**

## Goal

Demonstrate the common location and simulation framework for emergency response and hospital/service planning while preserving safety, uncertainty and controlled-data boundaries.

## v1 role

This track is part of the stable v1 release contract. It is complete only when its implementation, compatibility, quality, security/governance, operational and reproducibility evidence satisfy both this specification and every applicable blocking gate in `conductor/releases.json` and `conductor/v1-gate.json`.

## Dependencies


- `accessibility_network_engine_20260719`
- `facility_location_engine_20260718`
- `simulation_validation_engine_20260719`

## Scope

- Public/synthetic ambulance station, demand, fleet, travel and hospital handover benchmarks.
- Coverage, backup/double coverage, probabilistic availability and dynamic-relocation examples.
- Hospital/service location, capacity, referral, minimum volume, workforce and resilience scenarios.
- Static optimisation versus queueing/dispatch simulation validation.
- Efficiency, tail response, rurality, subgroup equity, resilience and cost reporting.

## Out of scope

- Operational deployment or live dispatch recommendations.
- Publishing sensitive operational demand, roster or vulnerability data.

## Requirements

- **R01.** Public benchmarks are clearly separated from controlled operational analyses.
- **R02.** Response and service metrics include average, tail/worst-case, rural and subgroup results.
- **R03.** Vehicle/staff availability, handover and queueing assumptions are explicit.
- **R04.** Hospital models represent service type, capacity, workforce, referral and transition costs.
- **R05.** Safety review can block publication or operational interpretation.

## Acceptance criteria

- [ ] Ambulance benchmark includes maximal/backup coverage, busy availability and stochastic dispatch simulation.
- [ ] Dynamic relocation or posting is tested without implying live operational suitability.
- [ ] Hospital/service benchmark includes multiple services, capacity, referral/workforce, resilience and phased investment.
- [ ] Static and simulated results are compared under common scenarios and stress tests.
- [ ] Equity, rurality, tail outcomes and uncertainty are reported separately from averages.
- [ ] An independent multi-agent panel assesses operational/safety, methods and governance lenses and approves the bounded reference claims.

## Hardening and maturity gates

- M2 requires executable proof, negative tests and traceable evidence; interfaces may remain experimental.
- M3 requires real-data integration, migration evidence and representative failure handling.
- M4 requires repeated operation, external use, SLO evidence and bounded compatibility changes.
- M5 requires frozen interfaces, orchestrated agent-panel qualification, security/performance/recovery qualification and release-candidate soak.
- M6 requires supported compatibility, signed and preserved releases, external reproduction, named maintainers and post-release verification.
- Exceptions must be machine-readable, scoped, approved, time-limited and visible in release evidence.

## Evidence required

- Public/synthetic benchmark datasets and scenario manifests.
- Optimisation, simulation, stress and equity reports.
- Controlled/public boundary and safety review.
- Reproducible research objects for ambulance and hospital/service examples.

## Risks

- Synthetic demand is mistaken for operational reality.
- Static travel times omit congestion or handover delays.
- Optimising response targets shifts harm to rural or marginalised communities.
- Hospital consolidation models omit workforce or minimum-volume effects.

## Completion rule

The track may enter `complete` only after every acceptance criterion is evidenced in `index.md`, all blocking dependencies are complete, required migrations and documentation are published, and the target release readiness evaluator reports no track-specific blocker.
