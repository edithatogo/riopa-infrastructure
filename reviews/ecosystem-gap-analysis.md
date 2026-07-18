# Ecosystem Gap Analysis

**Review date:** 18 July 2026  
**Scope:** representative connector, archive, corpus, rules-as-code, health-directory, social-data and ecosystem-documentation repositories owned by `edithatogo`.

## Executive finding

The ecosystem does not lack provenance, reproducibility or publication engineering. It has several strong but repository-specific implementations. The primary gap is a **shared, versioned interoperability profile** that makes capture evidence, transformations, legal/source assertions, quality evidence, rights decisions and publication objects composable across repositories.

The recommended strategy is therefore **adopt and map, not replace and rewrite**. RIOPA should preserve native evidence, emit a common event/snapshot profile beside it, and extract shared libraries only after two or more real repositories demonstrate the boundary.

## Existing strengths to retain

| Strength | Evidence in the ecosystem | RIOPA treatment |
|---|---|---|
| Connector/archive responsibility boundaries | `fyi-cli` owns source access and capture; `fyi-archive` owns orchestration and distribution | encode the boundary as component and event contracts; do not move network logic |
| Tamper-evident content provenance | `fyi-cli/crates/fyi-core/src/provenance.rs` maintains a SHA-256 payload hash chain | retain as integrity evidence and map records into common artifact/capture events |
| Release-level hashes and workflow evidence | `fyi-archive/scripts/gen_provenance.py` records source revision, environment, fetch window, lockfile and artifact hashes | extend with semantic lineage, rights, quality and research-object links |
| Code-first/data-light and licensing boundaries | `healthpoint-rs` keeps licensed payloads out of the repository and records redistribution state | make rights assertions mandatory and prevent adapters from broadening source rights |
| Portable structured outputs | Parquet, DuckDB, LanceDB, WARC/WACZ, JSON/JSONL and dataset cards are already used across repositories | register each as a materialisation with purpose, source snapshot and declared fidelity/loss |
| Source-pinned legal and policy work | `rulespec-nz` uses corpus citation paths, pinned SHAs and ratcheted validation gaps | preserve citation paths; add provision/entity identity and transformation lineage |
| Reproducible corpus publication | `corpus-legislation-nz` separates raw XML/HTML, normalised records, Parquet shards, manifests, HF live data and DOI snapshots | map capture, transformation, snapshot, materialisation and release stages into one profile |
| Source metadata and cache validation | `open_social_data` records source URLs, quality reports, ETags and Last-Modified values | standardise source/capture/change metadata and expose it through the common catalogue |
| Modular analytical ecosystem | `ecosystem-docs` already presents interoperable HEOR, simulation and cross-domain tools | add RIOPA as the data/provenance/spatial substrate rather than a replacement umbrella |

## Priority gaps

### G1. Cross-repository identity and provenance profile — critical

There is no shared identifier or schema for source, capture, artifact, run, snapshot, materialisation, quality result or release across the ecosystem. Native evidence cannot yet be joined without project-specific code.

**Response:** the schemas in `schemas/`, URI patterns in `docs/architecture.md`, and the `provenance_profile_v1_20260718` track.

### G2. Semantic transformation lineage — critical

Current provenance is strongest at content integrity and release packaging. It is less consistent for transformation semantics: exact input partitions, parameters, exclusions, manual decisions, ontology/model versions, declared losses and affected rows/features.

**Response:** transformation-run records, three lineage granularity levels, manual-activity events, and required implementation/environment identities.

### G3. Bitemporal and legal-state modelling — critical for spatial/policy work

Retrieval time, source publication time, source-edit time, legal validity/effect and supersession are frequently different. A single `updated_at` field cannot support historical zoning or policy analyses.

**Response:** separate recorded/retrieved and valid/effective intervals, sourced status assertions, revision links and confidence/evidence fields.

### G4. Geospatial source and canonical layers — critical new capability

The reviewed ecosystem has facility/location data and spatial use cases, but not a national, versioned registry of council GIS/ePlan services, planning documents, zone/overlay semantics, geometry quality and spatial-to-rule links.

**Response:** `nz_spatial_source_registry_20260718`, `nz_spatial_archive_mvp_20260718`, `planning_rules_linkage_20260718` and `spatial_quality_temporality_20260718`.

### G5. Materialisation governance — high

Multiple useful output formats are present, but the relationship between canonical truth and optimised copies is not uniformly machine-readable. This creates a risk that DuckDB, LanceDB, Parquet or a vector index becomes an undocumented second source of truth.

**Response:** immutable snapshot manifests plus materialisation records specifying purpose, build inputs, reproducibility class, fidelity and known losses.

### G6. Unified quality evidence and waiver policy — high

Repositories have validation and quality reports, but metric identity, thresholds, applicability, failures, waivers and reviewer decisions are not yet portable across domains.

**Response:** versioned quality metrics, evidence artifacts, explicit `pass/warn/fail/not_applicable/waived` status, waiver reasons and ratcheting rules.

### G7. Automated methods and citable research objects — high

Several repositories publish to Zenodo/Hugging Face and maintain citation metadata. A downstream author still cannot reliably generate a paper methods statement and full supplement from one common release object.

**Response:** RO-Crate/Workflow Run RO-Crate, DataCite-ready metadata, rights inventory, quality summary, generated methods and clean-room rebuild report.

### G8. Cross-language conformance and migration — high

The ecosystem spans Rust, Python, Go and other languages. A Python-only library would not establish an interoperable contract.

**Response:** JSON Schema as the normative wire contract, language-neutral golden fixtures, generated native models where useful, and cross-language validation before profile v1 is stable.

### G9. Programme catalogue and dependency graph — medium/high

Conductor tracks are strong within repositories, and GitHub Projects coordinate selected programmes, but there is no common machine-readable inventory connecting repositories, releases, schemas, datasets, tracks, source systems and downstream dependencies.

**Response:** catalogue and PROV/RO-Crate projections from authoritative manifests; retain GitHub/Conductor as workflow surfaces rather than making a graph database operationally mandatory.

### G10. Māori data sovereignty and public/controlled-data separation — critical governance gap

Open-source licensing alone is not a sufficient governance model for data about Māori, small populations, places or communities. Public aggregate data and controlled/sensitive data require different architectures and decision rights.

**Response:** a dedicated governance track, source-level rights assertions, Māori data sovereignty review points, community/authority roles, disclosure review, and a separate controlled-data deployment profile.

### G11. Reusable spatial decision analytics — medium after data spine

Location-allocation, accessibility, emergency response simulation and MCDA are not yet exposed as one domain-neutral, provenance-aware engine.

**Response:** establish the spatial/source spine first, then implement p-median, p-center, set/maximal covering, capacitated and robust/multi-objective models with simulation adapters and explicit policy weights.

## Recommended adoption ladder

| Level | Requirement |
|---|---|
| A0 | Native repository evidence only; no RIOPA output |
| A1 | Source/artifact identities, rights state and capture/release event mapping |
| A2 | Transformation records, parameters, environment and quality evidence |
| A3 | Immutable snapshot manifest, materialisation registry and generated methods |
| A4 | RO-Crate/DOI release, attestations and independent rebuild evidence |

Initial targets:

| Repository | Current indicative level | First target | Reason |
|---|---:|---:|---|
| `fyi-cli` | A0 with strong native integrity evidence | A2 | prove Rust capture-event mapping without replacing its hash chain |
| `fyi-archive` | A1-like native release evidence | A4 | strongest candidate for a full research-object release demonstration |
| `corpus-legislation-nz` | A1/A2-like native corpus evidence | A3 | test legal-source, corpus and HF/DOI mappings |
| `nlp-policy-nz` | A1-like publication support | A3 | test model/ontology/chunk/source-span transformation lineage |
| `healthpoint-rs` | A1-like rights-aware export evidence | A2 | test licensed/open boundaries and facility assertions |
| `open_social_data` | A1-like source/catalogue evidence | A2 | test provider metadata, cache/change evidence and quality mapping |
| `rulespec-nz` | A1/A2-like source-pinned rule evidence | A3 | test provision identity, rule lineage and ratcheted gaps |

These levels are an architectural review, not a certification of the repositories. Formal conformance begins only after the profile and test suite are ratified.

## What not to do

- Do not replace existing native provenance with a lower-fidelity common record.
- Do not start with a compulsory graph database.
- Do not make LanceDB the primary spatial or legal store.
- Do not promise feature-level lineage where identifiers or transformations cannot support it.
- Do not harmonise council zone labels into a national class without retaining the original class, plan, rule links and mapping evidence.
- Do not let a generated methods narrative conceal missing facts; missing evidence must remain explicit.
- Do not treat all public web content as redistributable data.

## Decision

Proceed with the shared RIOPA profile and NZ spatial reference implementation. Extract separate `riopa-provenance`, spatial connector and decision-engine packages only after demonstrated reuse makes their interfaces stable.
