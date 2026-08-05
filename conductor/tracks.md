# Project Tracks

This is the programme-level source of truth for the stablehardened and supported RIOPA v1 roadmap. Each track has a specificationphased implementation planvalidated metadata and evidence index.

## Status summary

- **Total tracks:** 28
- **Complete:** 0
- **Active:** 0
- **Validating:** 0
- **Ready:** 0
- **Specified:** 28
- **Proposed:** 0
- **V1-critical:** 28

Track completion is not equivalent to release readiness. Stable v1 additionally requires the machine-readable maturitycross-track and release-authority gates in `conductor/maturity-model.json``conductor/releases.json` and `conductor/v1-gate.json`.

## Foundation

- [~] **`foundation_architecture_20260718`** — Foundation architecture and programme governance (target `0.3.0`current `M1`target `M6`risk High; depends on: none)
- [~] **`governance_maori_data_sovereignty_20260718`** — Rightsprivacy and Māori data sovereignty framework (target `0.3.0`current `M1`target `M6`risk Critical; depends on: `foundation_architecture_20260718`)
- [ ] **`security_supply_chain_20260719`** — Securityintegrity and software supply-chain hardening (target `0.3.0`current `M1`target `M6`risk Critical; depends on: `foundation_architecture_20260718`)
- [ ] **`operations_preservation_sre_20260719`** — Operationsservice reliability and digital preservation (target `0.8.0`current `M1`target `M6`risk Critical; depends on: `foundation_architecture_20260718``security_supply_chain_20260719`)

## Core

- [ ] **`canonical_domain_schemas_ontology_20260719`** — Canonical domain schemasidentifiers and ontology (target `0.3.0`current `M1`target `M6`risk High; depends on: `foundation_architecture_20260718``governance_maori_data_sovereignty_20260718`)
- [ ] **`provenance_profile_v1_20260718`** — Shared provenancetransformation and quality profile v1 (target `0.3.0`current `M1`target `M6`risk Critical; depends on: `foundation_architecture_20260718``security_supply_chain_20260719`)
- [ ] **`connector_runtime_capture_20260719`** — Common connector runtime and faithful capture framework (target `0.4.0`current `M1`target `M6`risk Critical; depends on: `provenance_profile_v1_20260718``governance_maori_data_sovereignty_20260718``security_supply_chain_20260719`)
- [ ] **`methods_research_objects_20260718`** — Research objectsmethods supplements and citation automation (target `0.4.0`current `M1`target `M6`risk Critical; depends on: `provenance_profile_v1_20260718``security_supply_chain_20260719`)
- [ ] **`repository_template_adoption_20260718`** — Repository template and cross-repository adoption (target `0.5.0`current `M1`target `M6`risk High; depends on: `provenance_profile_v1_20260718``methods_research_objects_20260718``security_supply_chain_20260719`)
- [ ] **`provenance_query_api_20260719`** — Queryable provenance and impact-analysis API (target `0.6.0`current `M1`target `M6`risk High; depends on: `canonical_domain_schemas_ontology_20260719``provenance_profile_v1_20260718`)

## NZ Spatial

- [ ] **`nz_spatial_source_registry_20260718`** — New Zealand spatial source and authority registry (target `0.4.0`current `M1`target `M6`risk High; depends on: `canonical_domain_schemas_ontology_20260719``provenance_profile_v1_20260718``governance_maori_data_sovereignty_20260718`)
- [ ] **`nz_spatial_archive_mvp_20260718`** — New Zealand Spatial Archive real-data vertical slice (target `0.5.0`current `M1`target `M6`risk Critical; depends on: `connector_runtime_capture_20260719``nz_spatial_source_registry_20260718``methods_research_objects_20260718``canonical_domain_schemas_ontology_20260719`)
- [ ] **`planning_rules_linkage_20260718`** — Council planning spatial-to-rule linkage (target `0.6.0`current `M1`target `M6`risk Critical; depends on: `nz_spatial_archive_mvp_20260718``canonical_domain_schemas_ontology_20260719`)
- [ ] **`planning_system_transition_20260719`** — Planning-system transition and legal continuity (target `0.7.0`current `M1`target `M6`risk Critical; depends on: `planning_rules_linkage_20260718``canonical_domain_schemas_ontology_20260719`)
- [ ] **`spatial_quality_temporality_20260718`** — Spatial qualitytemporality and change-analysis framework (target `0.7.0`current `M1`target `M6`risk High; depends on: `nz_spatial_archive_mvp_20260718``planning_rules_linkage_20260718``provenance_query_api_20260719`)
- [ ] **`nz_spatial_archive_operations_20260719`** — National archive coverageupdates and operations (target `0.8.0`current `M1`target `M6`risk Critical; depends on: `nz_spatial_archive_mvp_20260718``spatial_quality_temporality_20260718``operations_preservation_sre_20260719``nz_spatial_source_registry_20260718`)

## Analytics

- [ ] **`accessibility_network_engine_20260719`** — Multimodal accessibility and travel-matrix engine (target `0.6.0`current `M1`target `M6`risk High; depends on: `canonical_domain_schemas_ontology_20260719``provenance_profile_v1_20260718`)
- [ ] **`facility_registry_20260719`** — Versioned multi-source facility registry (target `0.6.0`current `M1`target `M6`risk High; depends on: `canonical_domain_schemas_ontology_20260719``connector_runtime_capture_20260719``governance_maori_data_sovereignty_20260718`)
- [ ] **`facility_location_engine_20260718`** — Inspectable facility-location and allocation engine (target `0.7.0`current `M1`target `M6`risk Critical; depends on: `canonical_domain_schemas_ontology_20260719``accessibility_network_engine_20260719`)
- [ ] **`simulation_validation_engine_20260719`** — Stochastic service simulation and model validation engine (target `0.8.0`current `M1`target `M6`risk Critical; depends on: `canonical_domain_schemas_ontology_20260719``facility_location_engine_20260718`)

## Applications

- [ ] **`emergency_health_facilities_pilot_20260718`** — Ambulance and hospital facility-planning reference pilots (target `0.8.0`current `M1`target `M6`risk Critical; depends on: `accessibility_network_engine_20260719``facility_location_engine_20260718``simulation_validation_engine_20260719``governance_maori_data_sovereignty_20260718`)
- [ ] **`health_outcomes_causal_methods_20260719`** — Health-outcomesspatial epidemiology and causal-methods framework (target `0.8.0`current `M1`target `M6`risk Critical; depends on: `governance_maori_data_sovereignty_20260718``spatial_quality_temporality_20260718``accessibility_network_engine_20260719`)
- [ ] **`supermarket_health_pilot_20260718`** — Supermarket accesszoning and health-geography reference study (target `0.8.0`current `M1`target `M6`risk High; depends on: `planning_rules_linkage_20260718``accessibility_network_engine_20260719``facility_registry_20260719``facility_location_engine_20260718``health_outcomes_causal_methods_20260719``governance_maori_data_sovereignty_20260718`)

## Publication

- [x] **`documentation_developer_experience_20260719`** — Documentationdeveloper experience and user support readiness (target `0.9.0`current `M1`target `M6`risk High; depends on: `repository_template_adoption_20260718``methods_research_objects_20260718``provenance_query_api_20260719``interoperability_conformance_sdks_20260719``nz_spatial_archive_operations_20260719``accessibility_network_engine_20260719``facility_location_engine_20260718`)
- [ ] **`publication_validation_20260718`** — Independent validationrelease and publication programme (target `0.9.0`current `M1`target `M6`risk High; depends on: `repository_template_adoption_20260718``nz_spatial_archive_mvp_20260718``methods_research_objects_20260718``security_supply_chain_20260719`)

## Release

- [ ] **`performance_scalability_reliability_20260719`** — Performancescalability and reliability qualification (target `0.9.0`current `M1`target `M6`risk Critical; depends on: `connector_runtime_capture_20260719``provenance_query_api_20260719``nz_spatial_archive_operations_20260719``accessibility_network_engine_20260719``facility_location_engine_20260718``simulation_validation_engine_20260719``operations_preservation_sre_20260719`)
- [x] **`v1_release_hardening_20260719`** — Stable v1 release hardening and general availability (target `1.0.0`current `M1`target `M6`risk Critical; depends on: `accessibility_network_engine_20260719``canonical_domain_schemas_ontology_20260719``connector_runtime_capture_20260719``documentation_developer_experience_20260719``emergency_health_facilities_pilot_20260718``facility_location_engine_20260718``facility_registry_20260719``foundation_architecture_20260718``governance_maori_data_sovereignty_20260718``health_outcomes_causal_methods_20260719``interoperability_conformance_sdks_20260719``methods_research_objects_20260718``nz_spatial_archive_mvp_20260718``nz_spatial_archive_operations_20260719``nz_spatial_source_registry_20260718``operations_preservation_sre_20260719``performance_scalability_reliability_20260719``planning_rules_linkage_20260718``planning_system_transition_20260719``provenance_profile_v1_20260718``provenance_query_api_20260719``publication_validation_20260718``repository_template_adoption_20260718``security_supply_chain_20260719``simulation_validation_engine_20260719``spatial_quality_temporality_20260718``supermarket_health_pilot_20260718`)

## Critical-path and parallelisation rule

Normative contractsgovernancesecurity and faithful capture are upstream of publication. Accessibilityoptimisationsimulationperformance and conformance implementations may progress against synthetic or public benchmarks in parallelbut they cannot close without real-data integrationmigrationoperational and independent-verification evidence.

## Stable v1 completion

Stable v1.0 requires every v1-critical track to reach its declared maturity targetall blocking `1.0.0` gates to passthe global v1 gate to passno prohibited defect or expired waiverand a signed release-authority decision. See `docs/v1-definition-of-done.md`.

*Programme configuration version: 0.2.0*  
*Updated: 2026-07-19*
