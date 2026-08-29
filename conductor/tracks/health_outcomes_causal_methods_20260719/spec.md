# Track: Health-outcomes, spatial epidemiology and causal-methods framework

Track ID: `health_outcomes_causal_methods_20260719`  
Phase: **Applications**  
Target release: **0.8.0**  
Maturity target: **M6**  
Stability class: **Reference**  
V1 critical: **yes**

## Goal

Provide a rigorous framework for linking access, zoning and facilities to health outcomes while separating ecological description, prediction, causal inference and prescriptive modelling.

## v1 role

This track is part of the stable v1 release contract. It is complete only when its implementation, compatibility, quality, security/governance, operational and reproducibility evidence satisfy both this specification and every applicable blocking gate in `conductor/releases.json` and `conductor/v1-gate.json`.

## Dependencies


- `spatial_quality_temporality_20260718`
- `accessibility_network_engine_20260719`

## Scope

- Causal DAGs, estimands, exposure/outcome definitions and analysis registries.
- Ecological, multilevel, longitudinal, event-study, interrupted-time-series and quasi-experimental options.
- Spatial confounding, autocorrelation, MAUP, boundary change and measurement error.
- Negative controls, missing data, sensitivity, subgroup/equity and multiplicity.
- Privacy, small cells, public/controlled data boundaries and preregistration.

## Out of scope

- Claiming individual causal effects from cross-sectional area-level associations.
- Publishing sensitive health unit records or unstable small-area estimates.

## Requirements

- **R01.** Every analysis declares whether it is descriptive, predictive, causal or prescriptive.
- **R02.** Causal analyses declare estimand, identification assumptions, DAG and falsification/sensitivity plan.
- **R03.** Boundary, denominator, exposure and outcome versions are fixed in the analysis manifest.
- **R04.** Spatial dependence and ecological limitations are assessed rather than mentioned generically.
- **R05.** Results suppress or control sensitive small cells and governance triggers.

## Acceptance criteria

- [ ] A machine-readable analysis protocol captures DAG, estimand, population, exposure, comparator, outcome, time and assumptions.
- [ ] Reference code supports descriptive spatial analysis and at least one longitudinal/quasi-experimental design on public or synthetic data.
- [ ] Spatial confounding, autocorrelation, MAUP and measurement-error sensitivity are demonstrated.
- [ ] Negative control, missing-data and subgroup/equity plans are included where applicable.
- [ ] Preregistered pilot analyses distinguish exploratory from confirmatory results.
- [ ] An orchestrated methods-and-governance agent panel advises on claims and recommends bounded language; the sole developer records the disposition, and no human peer or external approval is claimed.

## Hardening and maturity gates

- M2 requires executable proof, negative tests and traceable evidence; interfaces may remain experimental.
- M3 requires real-data integration, migration evidence and representative failure handling.
- M4 requires repeated operation, representative agent-operated use, SLO evidence and bounded compatibility changes.
- M5 requires frozen interfaces, orchestrated agent-panel qualification, security/performance/recovery qualification and release-candidate soak.
- M6 requires supported compatibility, signed and preserved releases, isolated role-separated clean-room agent reproduction, named maintainers and post-release verification.
- Exceptions must be machine-readable, scoped, approved, time-limited and visible in release evidence.

## Evidence required

- Analysis protocol/estimand schema and DAG artifacts.
- Reference spatial and longitudinal methods implementations.
- Sensitivity, negative-control and MAUP reports.
- Preregistration and methods/governance agent-panel qualification.

## Risks

- Area-level confounding creates compelling but spurious associations.
- Store openings/closures are endogenous to community change.
- Health outcome availability or denominator quality varies geographically.
- Spatial precision creates privacy or group harm.

## Completion rule

The track may enter `complete` only after every acceptance criterion is evidenced in `index.md`, all blocking dependencies are complete, required migrations and documentation are published, and the target release readiness evaluator reports no track-specific blocker.
