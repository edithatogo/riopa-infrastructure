# Project Tracks

This file is the programme-level index for RIOPA Infrastructure. Each track has a detailed specification, phased plan, metadata and evidence index.

## Status summary

- **Total tracks:** 13
- **Complete:** 0
- **Active:** 0
- **Specified/proposed:** all tracks below

## Foundation

- [ ] **foundation_architecture_20260718** — Foundation architecture and programme governance (depends on: none)
- [ ] **governance_maori_data_sovereignty_20260718** — Rights, privacy and Māori data sovereignty framework (depends on: `foundation_architecture_20260718`)

## Core

- [ ] **provenance_profile_v1_20260718** — Shared provenance, transformation and quality profile v1 (depends on: `foundation_architecture_20260718`)
- [ ] **methods_research_objects_20260718** — Research objects, methods supplements and citation automation (depends on: `provenance_profile_v1_20260718`)
- [ ] **repository_template_adoption_20260718** — Repository template and cross-repository adoption (depends on: `provenance_profile_v1_20260718`, `methods_research_objects_20260718`)

## NZ Spatial

- [ ] **nz_spatial_source_registry_20260718** — New Zealand spatial source and authority registry (depends on: `provenance_profile_v1_20260718`, `governance_maori_data_sovereignty_20260718`)
- [ ] **nz_spatial_archive_mvp_20260718** — New Zealand Spatial Archive minimum viable release (depends on: `nz_spatial_source_registry_20260718`, `methods_research_objects_20260718`)
- [ ] **planning_rules_linkage_20260718** — Council planning spatial-to-rule linkage (depends on: `nz_spatial_archive_mvp_20260718`)
- [ ] **spatial_quality_temporality_20260718** — Spatial quality, temporality and change-analysis framework (depends on: `nz_spatial_archive_mvp_20260718`, `planning_rules_linkage_20260718`)

## Analytics

- [ ] **facility_location_engine_20260718** — Domain-neutral accessibility and facility-location engine (depends on: `spatial_quality_temporality_20260718`)

## Applications

- [ ] **supermarket_health_pilot_20260718** — Supermarket access, zoning and health geography pilot (depends on: `planning_rules_linkage_20260718`, `facility_location_engine_20260718`, `governance_maori_data_sovereignty_20260718`)
- [ ] **emergency_health_facilities_pilot_20260718** — Ambulance and hospital facility planning pilot (depends on: `facility_location_engine_20260718`, `governance_maori_data_sovereignty_20260718`)

## Publication

- [ ] **publication_validation_20260718** — Independent validation, releases and publication programme (depends on: `repository_template_adoption_20260718`, `nz_spatial_archive_mvp_20260718`)

---

*Created: 2026-07-18*
*Programme version: 0.1.0*
