# Track: Inspectable facility-location and allocation engine

Track ID: `facility_location_engine_20260718`  
Phase: **Analytics**  
Target release: **0.7.0**  
Maturity target: **M6**  
Stability class: **Platform**  
V1 critical: **yes**

## Goal

Provide reusable, independently verifiable optimisation for coverage, average access, worst-case equity, capacity, competition, robustness and multi-period decisions.

## v1 role

This track is part of the stable v1 release contract. It is complete only when its implementation, compatibility, quality, security/governance, operational and reproducibility evidence satisfy both this specification and every applicable blocking gate in `conductor/releases.json` and `conductor/v1-gate.json`.

## Dependencies


- `canonical_domain_schemas_ontology_20260719`
- `accessibility_network_engine_20260719`

## Scope

- Language-neutral demand, candidate, cost, capacity, eligibility, objective and solution contracts.
- Set covering, maximal covering, p-median, p-center and capacitated formulations.
- Competitive/market-capture, multi-period, opening/closure and resilience extensions.
- Equity constraints, robust/stochastic scenarios and Pareto/epsilon-constraint workflows.
- Solver provenance, bounds, tolerances, seeds, independent feasibility and result explanation.

## Out of scope

- Hiding stakeholder values in one default weighted score.
- Using static optimisation where dispatch, queueing or congestion requires simulation.

## Requirements

- **R01.** Mathematical model, policy scenario and stakeholder preference layers are separate.
- **R02.** Every solution includes solver identity, status, bound, gap, tolerance, seed and constraint residuals.
- **R03.** An independent verifier checks feasibility and objective values.
- **R04.** Infeasible models return diagnostic conflicts or bounded explanations.
- **R05.** Equity alternatives are reported as explicit constraints/objectives and Pareto choices.

## Acceptance criteria

- [ ] Reference formulations cover set cover, maximal cover, p-median, p-center and capacitated location under one problem contract.
- [ ] Competitive, robust, equity and multi-period examples are implemented or explicitly excluded from v1 with rationale.
- [ ] Public benchmark instances match known optima/bounds or trusted references.
- [ ] Independent feasibility and objective verification catches intentionally corrupted solutions.
- [ ] Performance and memory budgets are met for representative national scenarios.
- [ ] MCDA consumes transparent alternatives and never changes the mathematical solution silently.

## Hardening and maturity gates

- M2 requires executable proof, negative tests and traceable evidence; interfaces may remain experimental.
- M3 requires real-data integration, migration evidence and representative failure handling.
- M4 requires repeated operation, external use, SLO evidence and bounded compatibility changes.
- M5 requires frozen interfaces, orchestrated agent-panel qualification, security/performance/recovery qualification and release-candidate soak.
- M6 requires supported compatibility, signed and preserved releases, external reproduction, named maintainers and post-release verification.
- Exceptions must be machine-readable, scoped, approved, time-limited and visible in release evidence.

## Evidence required

- Problem/solution schemas and mathematical specifications.
- Public benchmark corpus and solver comparison.
- Independent verifier and corrupted-solution negative tests.
- Performance, equity, robustness and infeasibility reports.

## Risks

- Solver-specific features leak into the stable contract.
- A mathematically optimal result is operationally infeasible.
- Equity choices are obscured by normalisation or weights.
- Large robust/multi-period models become computationally intractable.

## Completion rule

The track may enter `complete` only after every acceptance criterion is evidenced in `index.md`, all blocking dependencies are complete, required migrations and documentation are published, and the target release readiness evaluator reports no track-specific blocker.
