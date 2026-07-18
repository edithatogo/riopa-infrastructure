# ADR-0002: Append-Only Event Log as Provenance Backbone

- **Status:** Accepted for v0.1
- **Date:** 2026-07-18

## Context

Directly writing a knowledge graph from every connector creates operational coupling and makes event repair difficult. File-only provenance is portable but hard to query across runs and repositories.

## Decision

Use a compact append-only event profile with canonical hashes. Project the events into W3C PROV, OpenLineage, DuckDB and optional graph stores. Snapshot manifests close the required lineage for a release.

## Consequences

- Projectors are deterministic and tested.
- Event schema evolution and migrations are required.
- The graph is disposable; the event stream and raw evidence are retained.
- Existing hash chains remain valid evidence and can be referenced/mapped.
