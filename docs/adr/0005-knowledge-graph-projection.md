# ADR-0005: Knowledge Graph as a Projection, Not an MVP Dependency

- **Status:** Accepted for v0.1
- **Date:** 2026-07-18

## Context

Cross-domain provenance is naturally graph-shaped, but a dedicated graph database adds deployment and maintenance burden before query demand is known.

## Decision

Emit PROV JSON-LD/RDF and relational lineage views from the event log. Add a graph database only after benchmarked queries justify it.

## Consequences

- Semantic interoperability is available from the first release.
- Local users can query lineage in DuckDB.
- No graph vendor or service becomes a preservation dependency.
