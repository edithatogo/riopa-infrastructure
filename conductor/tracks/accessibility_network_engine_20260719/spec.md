# Track: Multimodal accessibility and travel-matrix engine

Track ID: `accessibility_network_engine_20260719`  
Phase: **Analytics**  
Target release: **0.6.0**  
Maturity target: **M6**  
Stability class: **Platform**  
V1 critical: **yes**

## Goal

Provide reusable, versioned and benchmarked travel matrices and accessibility measures for walking, cycling, driving, public transport and capacity-aware service access.

## v1 role

This track is part of the stable v1 release contract. It is complete only when its implementation, compatibility, quality, security/governance, operational and reproducibility evidence satisfy both this specification and every applicable blocking gate in `conductor/releases.json` and `conductor/v1-gate.json`.

## Dependencies


- `canonical_domain_schemas_ontology_20260719`
- `provenance_profile_v1_20260718`

## Scope

- Origin, destination, network, timetable, impedance and travel-matrix contracts.
- Straight-line, road, walking, cycling and GTFS/public-transport workflows.
- Cumulative opportunity, gravity, two-step floating catchment and capacity-aware measures.
- Time-dependent, opening-hours, uncertainty, subgroup and scenario handling.
- Caching, partitioning, performance, benchmark and cross-engine validation.

## Out of scope

- Claiming routing accuracy where networks or timetables are incomplete.
- Embedding policy weights or facility-placement decisions in accessibility metrics.

## Requirements

- **R01.** Network and timetable inputs are immutable/versioned independently from facilities and demand.
- **R02.** Travel-matrix generation records engine, version, profile, parameters, time and exclusions.
- **R03.** Accessibility measures are explicit formulas with denominator and capacity semantics.
- **R04.** Unreachable, missing and censored travel times are distinct.
- **R05.** Approximation or caching errors are measured against a reference.

## Acceptance criteria

- [ ] A common contract supports straight-line and at least three network/public-transport modes.
- [ ] Reference implementations cover cumulative opportunity, gravity and two-step floating catchment measures.
- [ ] Opening hours, facility capacity, car ownership/rurality and uncertainty can be represented without hidden defaults.
- [ ] Public benchmark instances agree with trusted reference outputs within declared tolerances.
- [ ] Representative national-scale matrix workloads meet documented performance and cost budgets.
- [ ] Every output is traceable to network/timetable, demand, facility and parameter versions.

## Hardening and maturity gates

- M2 requires executable proof, negative tests and traceable evidence; interfaces may remain experimental.
- M3 requires real-data integration, migration evidence and representative failure handling.
- M4 requires repeated operation, representative agent-operated use, SLO evidence and bounded compatibility changes.
- M5 requires frozen interfaces, orchestrated agent-panel qualification, security/performance/recovery qualification and release-candidate soak.
- M6 requires supported compatibility, signed and preserved releases, isolated role-separated clean-room agent reproduction, named maintainers and post-release verification.
- Exceptions must be machine-readable, scoped, approved, time-limited and visible in release evidence.

## Evidence required

- Travel-matrix and accessibility specifications.
- Cross-engine benchmark and tolerance reports.
- Performance/cost benchmarks and cache validation.
- Mode, uncertainty and subgroup worked examples.

## Risks

- Proprietary networks or APIs restrict reproducibility.
- GTFS availability is incomplete or static schedules misrepresent service.
- Large matrices exceed local compute/storage budgets.
- Accessibility metrics are interpreted as actual utilisation or health effect.

## Completion rule

The track may enter `complete` only after every acceptance criterion is evidenced in `index.md`, all blocking dependencies are complete, required migrations and documentation are published, and the target release readiness evaluator reports no track-specific blocker.
