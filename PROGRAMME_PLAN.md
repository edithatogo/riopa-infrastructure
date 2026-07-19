# RIOPA Infrastructure: programme roadmap to stable v1.0

**Roadmap configuration:** 0.2.0  
**Updated:** 19 July 2026  
**Current programme maturity:** M1 — specified prototype  
**Target:** M6 — stable v1 general availability

## Mission

Build open, modular, provenance-first research infrastructure that converts heterogeneous public and appropriately governed data into citable, reproducible and maintainable research objects and decision analyses. The first full reference implementation is a temporally versioned New Zealand spatial and planning archive supporting supermarket and health geography, ambulance-system analysis and hospital-facility planning.

This roadmap deliberately distinguishes a convincing prototype from a mature release. The programme does not reach v1.0 merely because features exist. It reaches v1.0 only after its contracts, software, data operations, analytical methods, governance, security, performance, documentation, preservation and independent reproduction have all passed evidence-based gates.

## Stable-v1 contract

Stable v1.0 must be all of the following at the same time:

- **Semantically stable:** schemas, ontology, identifiers, APIs, CLI, configuration and materialisation contracts have version negotiation, compatibility guarantees and tested migration paths.
- **Scientifically defensible:** provenance, data quality, uncertainty, causal boundaries, optimisation assumptions, equity objectives and interpretation limits are explicit and independently reviewed.
- **Secure and trustworthy:** source capture, credentials, dependencies, builds, releases and incident response follow an exercised threat and supply-chain model.
- **Operational:** source change, scheduled updates, retries, quarantine, correction, backfill, monitoring, recovery and cost control have been exercised over repeated cycles.
- **Performant within bounds:** reference workloads meet published throughput, latency, resource, scale, resilience and cost envelopes without disabling evidence or correctness controls.
- **Interoperable:** at least two implementations and an independent consumer pass language-neutral conformance fixtures and standards-projection tests.
- **Preservable and citable:** releases contain complete research objects, methods, quality, rights, software/environment evidence, signatures, attestations, persistent identifiers and tested restoration.
- **Usable and supportable:** people outside the founding team can install, reproduce, operate, troubleshoot and extend supported workflows using released documentation and named support channels.
- **Governed:** rights, privacy, ethics, benefit, sensitive locations and Māori data sovereignty are release decisions, not afterthoughts.
- **Independently reproduced:** two clean-room reproductions, including one external operator, reproduce a real-data archive release and an applied analytical benchmark.

Feature completion without those properties is not v1.0.

## Programme architecture

The programme remains federated. Repositories may own connectors, archives, domain models or applications, while shared contracts make the outputs composable.

| Layer | Responsibility | Stability rule |
|---|---|---|
| L0 source evidence | Original responses, files, service definitions, documents, headers, terms and capability snapshots | Immutable and append-only |
| L1 provenance and canonical state | Acquisition and transformation events, stable identities, bitemporal entities, manual/AI review and rights/quality assertions | Versioned normative contracts |
| L2 materialisations | Parquet/GeoParquet, DuckDB Spatial, STAC, PMTiles, COG/Zarr, optional PostGIS and LanceDB indexes | Rebuildable projections |
| L3 analytics | Accessibility, facility reconciliation, optimisation, simulation, uncertainty and equity results | Versioned model specifications |
| L4 research objects | Methods, citations, quality, rights, environment, checksums, attestations and preservation records | Immutable signed release |

Raw evidence and append-only provenance are authoritative. Databases, graphs, indexes, tiles and publication bundles are deterministic or explicitly tolerance-bounded projections.

## Maturity model

| Level | Name | Exit meaning |
|---|---|---|
| M0 | Concept | Problem and intended benefit identified; no binding contract. |
| M1 | Specified prototype | Scope, risks, dependencies, interfaces, acceptance and evidence contracts validate. |
| M2 | Integrated alpha | Executable real or representative workflow, negative tests and traceable evidence exist; interfaces remain experimental. |
| M3 | Operational beta | Repeated cycles, migration, failure/recovery and external-use evidence exist. |
| M4 | Hardened beta | Security, performance, preservation, scientific and compatibility hardening pass; interfaces approach freeze. |
| M5 | Release candidate | Normative interfaces are frozen; candidate artifacts pass soak, independent reproduction and external workflow validation. |
| M6 | Stable v1 GA | Supported compatibility, named maintainers, signed and preserved releases and post-release obligations are in force. |

Maturity is assessed across 12 dimensions: governance, contracts, provenance, security, data, operations, performance, interoperability, publication, usability, analytics and science. No dimension can be silently averaged away by strength in another.

## Release train

| Release | Channel | Programme maturity | Purpose |
|---|---|---:|---|
| 0.2.0 | experimental | M1 | Machine-enforceable v1 roadmap, maturity model, evidence policy and 28-track Conductor graph |
| 0.3.0 | experimental | M2 | Normative governance, security, domain-schema/ontology and provenance core alpha |
| 0.4.0 | experimental | M2 | Real national-and-council capture through a complete research object |
| 0.5.0 | experimental | M3 | Bounded New Zealand spatial archive alpha with reproducible GeoParquet and DuckDB materialisations |
| 0.6.0 | candidate | M3 | Queryable lineage, planning-rule linkage, facility reconciliation, accessibility and cross-language interoperability beta |
| 0.7.0 | candidate | M4 | Hardened temporal planning, spatial quality and independently verified facility-location engine |
| 0.8.0 | candidate | M4 | Repeated archive operations, preservation, simulation validation and scientifically bounded applied pilots |
| 0.9.0 | release candidate | M5 | Full feature and contract freeze; security, performance, operations, documentation and independent-reproduction qualification |
| 1.0.0 | stable | M6 | Supported, signed, preserved and independently verified general availability |

Release readiness is evaluated from `conductor/releases.json`; stable-v1 thresholds are additionally fixed in `conductor/v1-gate.json`.

## Conductor programme

The 28 tracks are grouped into seven phases. Every track has a specification, phased implementation plan, machine-readable metadata and evidence index.

### Foundation

1. Programme architecture and release governance.
2. Rights, privacy, ethics and Māori data sovereignty.
3. Security, integrity and software supply-chain hardening.
4. Operations, preservation and site-reliability engineering.

### Core contracts and platform

5. Shared provenance, transformation and quality profile.
6. Canonical domain schemas and ontology.
7. Methods and research-object publication framework.
8. Common connector runtime and faithful capture.
9. Repository template and ecosystem adoption.
10. Provenance and impact-query API.
11. Interoperability, conformance suites and supported SDKs.

### New Zealand spatial and planning infrastructure

12. National spatial/planning source registry.
13. Real-data spatial archive MVP.
14. Spatial-to-planning-rule linkage.
15. Planning-system transition and legal continuity.
16. Spatial quality, identity and bitemporal reconstruction.
17. National archive automation and coverage operations.

### Reusable analytics

18. Accessibility and network-analysis engine.
19. Versioned multi-source facility registry.
20. Facility-location optimisation engine.
21. Simulation and validation engine.

### Applied validation

22. Health-outcomes and causal-method framework.
23. Supermarket access, zoning and health pilot.
24. Ambulance, emergency-response and hospital-facility pilot.

### Publication and release qualification

25. Documentation, developer experience and user support readiness.
26. Independent publication and clean-room validation.
27. Performance, scalability and reliability qualification.
28. Stable-v1 release hardening and general availability.

The complete dependency table is in `conductor/tracks.md`.

## Critical implementation path

### Stage A — ratify contracts before scaling

The programme first freezes the product boundary, decision rights, threat model, core identities, ontology and provenance semantics. Existing repositories are mapped field-by-field so that native evidence is preserved rather than overwritten by a new abstraction.

### Stage B — prove one difficult real vertical slice

Before national ingestion, one council GIS service, one district-plan document, one national spatial/population source and one facility source pass through:

```text
source discovery → faithful capture → immutable raw evidence →
canonical bitemporal entities → spatial-to-rule links →
GeoParquet and DuckDB → quality/rights reports →
methods and signed research object → clean-room reproduction
```

This stage is intentionally narrow and deep. It forces identity, pagination, geometry, legal-status, rights, temporal and packaging assumptions to meet real data.

### Stage C — make the evidence queryable and reusable

The next stage exposes dataset-, partition- and feature-level lineage only where justified; links spatial classes to sourced planning provisions; reconciles multiple facility assertions; and implements multimodal accessibility independently from facility optimisation.

### Stage D — validate decision methods before application

Set covering, maximal covering, p-median, p-center, capacity, competitive location, equity and robust/multi-objective formulations are benchmarked against independent solvers. Ambulance and hospital work additionally requires queueing, probabilistic availability, backup coverage, dynamic relocation, handover delay and multi-service referral-network simulation.

### Stage E — operate, harden and independently reproduce

The archive then completes repeated scheduled cycles, source changes, backfills, failures, restores, corrections and withdrawals. Release-candidate qualification adds security, malicious-input, performance, capacity, cost, cross-language, documentation, accessibility and external-reproduction evidence.

## Domain-specific research progression

### Supermarkets, zoning and health geography

The pilot separates seven distinct questions:

1. facility density;
2. physical accessibility by travel mode and time;
3. affordability and economic access;
4. healthy-food availability and store service range;
5. competition and market capture;
6. descriptive or causal association with area-level health outcomes;
7. counterfactual facility placement under planning, capacity, equity and cost constraints.

The facility registry preserves retailer, council, public-register and other source assertions separately, including disagreement, coordinates, opening/closure/relocation history, match evidence and rights. Health analysis distinguishes descriptive, predictive, causal and prescriptive claims; ecological and modifiable-area-unit limitations remain explicit.

### Ambulance services

The reference programme includes maximal and backup coverage, busy-fraction and probabilistic-availability formulations, queueing, time-dependent travel, fleet and roster constraints, dynamic relocation, dispatch simulation and ambulance–hospital handover delays. It is a research and planning reference, not a live dispatch system.

### Hospitals and clinical facilities

Hospital planning adds multi-service and hierarchical location, referral and transfer networks, workforce constraints, minimum safe clinical volumes, economies of scale, resilience/failover, phased capital investment and transition costs. Clinical-safety and service-policy judgements remain outside the optimisation engine and require accountable governance.

## Evidence and release control

Every track transition is supported by its `index.md`. Release evidence records identify the gate, evidence artifacts, reviewer, review date, expiry and any waiver. Stable v1 additionally requires:

- zero open P0 or P1 defects;
- zero release-blocking P2 defects;
- zero critical security findings;
- zero governance prohibitions;
- zero expired waivers;
- at least two independent reviewers;
- two clean-room reproductions, including one external;
- two external user workflows and one external operator workflow;
- at least three operational cycles;
- at least 90 consecutive days of representative operational evidence;
- at least 30 days of release-candidate soak;
- gate evidence no older than 120 days unless a stricter policy applies;
- immutable evidence identifiers and machine-readable release decisions;
- signed approvals from release management, security, governance, scientific-method and independent-reproducibility roles.

Critical security, governance prohibition, integrity failure and unresolved P0/P1 categories are not waivable. Other exceptions must be scoped, approved, mitigated, public where safe and expire within 90 days.

## V1 compatibility and maintenance

- Stable schema/API/CLI removals require a documented deprecation window and tested migration path.
- Immutable source captures, event hashes, historical assertions and released research objects never change in place.
- Scientific estimands, facility classifications, optimisation objectives and defaults are versioned independently from software patch releases.
- v1.0.x contains compatible defects, security and documentation fixes.
- Annual revalidation covers conformance, restore, preservation, dependencies, security and maintainer succession.
- A source or dataset can be corrected or withdrawn without erasing prior evidence; supersession remains explicit.

## Current delivery boundary

This 0.2.0 bundle delivers the architecture, machine-readable maturity/release/gate model, 28 Conductor tracks, evidence-aware roadmap validator, deterministic issue generation and the existing provenance/research-object prototype. Its own four M1 roadmap gates pass against the local evidence record. The programme as a whole nevertheless remains at M1. It does **not** claim that the national archive, accessibility engine, facility solvers, simulations, applied analyses, remote GitHub project or stable-v1 evidence already exist.

The next implementation milestone is the 0.3.0 normative core, followed immediately by the 0.4.0 real-data vertical slice. That sequence is the shortest credible path from the present M1 programme to a mature v1.0.


## Post-GA assurance loop

Stable v1 is an ongoing service and evidence commitment rather than a one-time tag. After 1.0.0:

- security, dependency, source-health, fixity, SLO and cost evidence is monitored continuously;
- critical corrections use signed 1.0.x releases with explicit supersession and no silent mutation of prior research objects;
- conformance, restore, preservation and maintainer-succession exercises are repeated at least annually;
- material source, legal, ontology or scientific-assumption changes trigger scoped requalification rather than inheriting the original approval automatically;
- unsupported surfaces are deprecated through the published policy and are never represented as supported merely because code remains available; and
- failure to sustain a stable obligation is published as a support-status change, with remediation, migration or archival guidance.
