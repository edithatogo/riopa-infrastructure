# Product Context

## Project

**RIOPA Infrastructure** — an open, modular, provenance-first research infrastructure ecosystem. It converts heterogeneous public and appropriately licensed data into citable, reproducible research objects and supports transparent spatial, policy, health, economic and operational decision analysis.

## Mission

Build once, verify continuously, reuse broadly: every source capture, transformation, quality decision, materialisation and release should be inspectable by humans, queryable by machines, and reproducible from preserved evidence.

## First reference implementation

The New Zealand Spatial Archive will harmonise and temporally version authoritative national geospatial data, council district-plan spatial layers, district-plan text, Gazette evidence, facility locations, population and area-level health outcomes.

## Initial applied questions

1. Where are supermarkets located relative to population, deprivation, transport and health outcomes?
2. Where could additional supermarkets improve access, subject to zoning and operational constraints?
3. How should ambulance bases or dynamic posting locations be configured under uncertain demand and response-time targets?
4. How should hospital or specialist-service locations, capacities and service portfolios be evaluated under efficiency, equity, resilience and budget constraints?

## Product goals

- A domain-neutral provenance profile adopted across connector, archive, corpus and analytics repositories.
- Research objects that generate both a concise citable methods statement and a publication-grade supplementary methods package.
- Reusable connectors and source registries rather than one-off scraping scripts.
- Faithful, immutable source capture separated from canonical harmonisation and derived analytics.
- Multiple physical representations without semantic drift.
- Temporal analysis across source publication, retrieval, legal validity and supersession.
- Public issue and Conductor-track graphs that expose dependencies, evidence and implementation status.

## Target users

- Health, policy, economic and geospatial researchers.
- Public agencies, councils, planners and service operators.
- Journalists, civil-society organisations and public-interest technologists.
- Software and data contributors who need stable contracts rather than a monolithic platform.

## Core capabilities

| Capability | Responsibility |
|---|---|
| Source discovery and access policy | Connector/source-registry modules |
| Faithful capture and change detection | Source-specific capture repositories |
| Shared event and lineage semantics | `riopa-provenance` core/profile |
| Canonical domain schemas | Domain packages, versioned independently |
| Snapshot orchestration and distribution | Archive repositories |
| Physical materialisations | Format adapters |
| Quality assessment | Shared quality contracts plus domain checks |
| Research-object and methods generation | Shared publication package |
| Optimisation and simulation | Domain-neutral decision engine |
| Applied studies | Separate, citable application repositories |

## Non-goals

- One central database that every project must use.
- Treating a search/vector database as archival truth.
- Republishing restricted data under a broader licence.
- Claiming legal authority for extracted zoning interpretations.
- Publishing sensitive unit-record health information.
- Hiding normative choices inside an optimisation objective or MCDA score.
