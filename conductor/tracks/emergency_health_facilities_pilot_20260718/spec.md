# Track: Ambulance and hospital facility planning pilot

Track ID: `emergency_health_facilities_pilot_20260718`  
Phase: **Applications**

## Goal

Demonstrate the common location framework for emergency response and health facilities while respecting operational data and safety boundaries.

## Dependencies

- `facility_location_engine_20260718`
- `governance_maori_data_sovereignty_20260718`

## Scope

- Public/synthetic benchmark scenarios for ambulance bases/dynamic posts.
- Discrete-event simulation validation of static location solutions.
- Hospital/service facility capacity and equity scenarios.
- Robustness to demand, travel-time and availability uncertainty.
- Controlled-data integration design without including restricted data in public releases.

## Out of scope

- Operational deployment recommendation from public aggregate data.
- Replacing clinical/operational governance.

## Acceptance criteria

- [ ] A synthetic/public benchmark demonstrates maximal covering and dynamic/simulation evaluation.
- [ ] Response-time, queueing, busy fraction, relocation and handover assumptions are explicit.
- [ ] Hospital scenarios include service/capacity and access-equity constraints.
- [ ] A controlled-data adapter contract is documented separately.
- [ ] Safety statement and non-operational boundary are prominent in all outputs.

## Risks

- Operational misuse.
- Demand data sensitivity.
- Simulation invalidity.
- Ignoring clinical service complementarities.
