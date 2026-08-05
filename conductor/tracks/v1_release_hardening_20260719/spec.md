# Track: Stable v1 release hardening and general availability

Track ID: `v1_release_hardening_20260719`  
Phase: **Release**  
Target release: **1.0.0**  
Maturity target: **M6**  
Stability class: **Governance**  
V1 critical: **yes**

## Goal

Freeze, audit, migrate, reproduce, operate and publish the complete programme as a supported stable v1.0 with explicit compatibility, security, service and scientific boundaries.

## v1 role

This track is part of the stable v1 release contract. It is complete only when its implementation, compatibility, quality, security/governance, operational and reproducibility evidence satisfy both this specification and every applicable blocking gate in `conductor/releases.json` and `conductor/v1-gate.json`.

## Dependencies


- `accessibility_network_engine_20260719`
- `canonical_domain_schemas_ontology_20260719`
- `connector_runtime_capture_20260719`
- `documentation_developer_experience_20260719`
- `emergency_health_facilities_pilot_20260718`
- `facility_location_engine_20260718`
- `facility_registry_20260719`
- `foundation_architecture_20260718`
- `governance_maori_data_sovereignty_20260718`
- `health_outcomes_causal_methods_20260719`
- `methods_research_objects_20260718`
- `nz_spatial_archive_mvp_20260718`
- `nz_spatial_archive_operations_20260719`
- `nz_spatial_source_registry_20260718`
- `operations_preservation_sre_20260719`
- `performance_scalability_reliability_20260719`
- `planning_rules_linkage_20260718`
- `planning_system_transition_20260719`
- `provenance_profile_v1_20260718`
- `provenance_query_api_20260719`
- `publication_validation_20260718`
- `repository_template_adoption_20260718`
- `security_supply_chain_20260719`
- `simulation_validation_engine_20260719`
- `spatial_quality_temporality_20260718`
- `supermarket_health_pilot_20260718`

## Scope

- V1 feature freeze, normative inventory, API/schema/ontology diff and compatibility tests.
- Performance, security, accessibility, documentation, governance and reproducibility audits.
- Upgrade, migration, rollback, restore, correction and withdrawal rehearsals.
- Release candidate soak, defect thresholds, external reproduction and user validation.
- Signed GA release, support/deprecation policy, maintainer roster and sustainability plan.

## Out of scope

- Adding new features after feature freeze unless required to fix a release blocker.
- Calling reference pilots operational or clinical decision systems.

## Requirements

- **R01.** The v1 release is defined by passed evidence gates, not a calendar date.
- **R02.** All normative interfaces are inventoried and compared against the previous candidate.
- **R03.** No P0/P1 defect remains and correctness/security/reproducibility P2 decisions are explicit.
- **R04.** Release artifacts are immutable, signed, preserved and independently verified.
- **R05.** Support, compatibility and maintenance obligations are bounded and resourced.

## Acceptance criteria

- [ ] All v1-critical tracks are complete with machine-readable evidence and no expired exception.
- [ ] Normative APIs, schemas, ontology, CLI, configuration and file formats pass frozen conformance suites.
- [ ] Upgrade, migration, rollback, restore, correction and withdrawal rehearsals pass on representative releases.
- [ ] Security, performance, operations, accessibility, documentation, governance and scientific audits have no unresolved blocker.
- [ ] Two clean-room reproductions, including one external operator, pass the release candidate.
- [ ] At least two external users complete distinct documented workflows.
- [ ] The stable release is signed, attested, checksummed, preserved, DOI-ready and accompanied by support/deprecation/sustainability policies.

## Hardening and maturity gates

- M2 requires executable proof, negative tests and traceable evidence; interfaces may remain experimental.
- M3 requires real-data integration, migration evidence and representative failure handling.
- M4 requires repeated operation, external use, SLO evidence and bounded compatibility changes.
- M5 requires frozen interfaces, independent review, security/performance/recovery qualification and release-candidate soak.
- M6 requires supported compatibility, signed and preserved releases, external reproduction, named maintainers and post-release verification.
- Exceptions must be machine-readable, scoped, approved, time-limited and visible in release evidence.

## Evidence required

- V1 normative inventory and frozen conformance suite.
- Defect, exception, audit and release-readiness reports.
- Migration/rollback/restore/withdrawal rehearsal evidence.
- External reproduction and user-validation reports.
- Signed release, preservation, support and maintainer records.

## Risks

- Release pressure weakens evidence gates.
- Late contract changes invalidate cross-repository adopters.
- A stable support promise exceeds maintainer capacity.
- Reference data coverage is mistaken for completeness or authority.

## Completion rule

The track may enter `complete` only after every acceptance criterion is evidenced in `index.md`, all blocking dependencies are complete, required migrations and documentation are published, and the target release readiness evaluator reports no track-specific blocker.
