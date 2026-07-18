# Track: Domain-neutral accessibility and facility-location engine

Track ID: `facility_location_engine_20260718`  
Phase: **Analytics**

## Goal

Provide reusable, inspectable optimisation components for coverage, average access, worst-case equity, capacity, competition and uncertainty.

## Dependencies

- `spatial_quality_temporality_20260718`

## Scope

- Set covering, maximal covering, p-median, p-center and capacitated models.
- Network/travel-time matrices and uncertainty.
- Multi-objective Pareto/epsilon-constraint workflows.
- MCDA as an explicit preference/deliberation layer.
- Solver-independent problem/result contracts and verification.

## Out of scope

- A hidden one-size-fits-all objective.
- Operational ambulance recommendations without simulation.

## Acceptance criteria

- [ ] Reference instances match known optimal solutions or certified bounds.
- [ ] Problem definitions separate demand, candidates, feasibility, capacity, objectives and equity groups.
- [ ] Every solution records solver/version, tolerances, seed, status and independent feasibility checks.
- [ ] Pareto alternatives and subgroup outcomes are reportable.
- [ ] At least supermarket and emergency-service adapters use the same core contracts.

## Risks

- Solver lock-in.
- Incorrect travel-time matrix.
- Normative weights hidden in defaults.
- Scalability.
