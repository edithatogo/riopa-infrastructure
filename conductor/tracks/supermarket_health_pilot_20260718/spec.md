# Track: Supermarket access, zoning and health-geography reference study

Track ID: `supermarket_health_pilot_20260718`  
Phase: **Applications**  
Target release: **0.8.0**  
Maturity target: **M6**  
Stability class: **Reference**  
V1 critical: **yes**

## Goal

Reproduce and extend supermarket density/access analysis with open code, multi-source facilities, zoning feasibility, health outcomes, causal restraint and transparent location alternatives.

## v1 role

This track is part of the stable v1 release contract. It is complete only when its implementation, compatibility, quality, security/governance, operational and reproducibility evidence satisfy both this specification and every applicable blocking gate in `conductor/releases.json` and `conductor/v1-gate.json`.

## Dependencies


- `planning_rules_linkage_20260718`
- `accessibility_network_engine_20260719`
- `facility_registry_20260719`
- `facility_location_engine_20260718`
- `health_outcomes_causal_methods_20260719`

## Scope

- Reproduction of geography- and population-density supermarket findings.
- Multi-source supermarket assertions, classification and temporal registry.
- Distance, network, multimodal, capacity, competition and deprivation access measures.
- Planning-rule feasibility and candidate-site construction.
- Area-level health analysis, uncertainty, optimisation alternatives and publication package.

## Out of scope

- Attributing individual health outcomes to supermarket placement from ecological association alone.
- Publishing a commercial site recommendation without market, land, community and feasibility review.

## Requirements

- **R01.** Reproduction and extension are separated, with discrepancies documented.
- **R02.** Density, accessibility, affordability/availability, competition and health association remain distinct constructs.
- **R03.** Candidate feasibility is sourced from linked rules and caveated where consent discretion remains.
- **R04.** Descriptive, causal and prescriptive outputs use distinct analysis manifests.
- **R05.** Optimisation reports multiple equity/efficiency alternatives rather than one preferred answer.

## Acceptance criteria

- [ ] The baseline density/population analysis is reproduced from public, versioned inputs or discrepancies are fully explained.
- [ ] Facility reconciliation and accessibility sensitivity are agent-panel qualified.
- [ ] Planning feasibility cites source provisions and represents overlays, status and uncertainty.
- [ ] Health analyses comply with the causal-methods framework and make ecological limitations prominent.
- [ ] Location alternatives report average, worst-case, subgroup, capacity, competition, cost and robustness trade-offs.
- [ ] Code, data or resolvable inputs, methods, quality, governance and research object pass isolated multi-agent clean-room reproduction.

## Hardening and maturity gates

- M2 requires executable proof, negative tests and traceable evidence; interfaces may remain experimental.
- M3 requires real-data integration, migration evidence and representative failure handling.
- M4 requires repeated operation, external use, SLO evidence and bounded compatibility changes.
- M5 requires frozen interfaces, orchestrated agent-panel qualification, security/performance/recovery qualification and release-candidate soak.
- M6 requires supported compatibility, signed and preserved releases, external reproduction, named maintainers and post-release verification.
- Exceptions must be machine-readable, scoped, approved, time-limited and visible in release evidence.

## Evidence required

- Preregistered reproduction/extension protocol.
- Facility, access, zoning and health analysis packages.
- Sensitivity, equity, causal-limitation and governance reports.
- Complete research object and isolated multi-agent clean-room reproduction by the required subagent panel.

## Risks

- Original study details or data are unavailable.
- Facility classification materially changes conclusions.
- Zoning permission is confused with commercial viability or consent certainty.
- Health associations are overinterpreted in public communication.

## Completion rule

The track may enter `complete` only after every acceptance criterion is evidenced in `index.md`, all blocking dependencies are complete, required migrations and documentation are published, and the target release readiness evaluator reports no track-specific blocker.
