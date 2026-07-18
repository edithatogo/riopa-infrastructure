# ADR-0003: Logical Snapshots with Multiple Disposable Materialisations

- **Status:** Accepted for v0.1
- **Date:** 2026-07-18

## Context

Researchers benefit from Parquet, DuckDB, LanceDB, web tiles and service databases. Treating each output as a separately curated dataset invites drift.

## Decision

Define one immutable logical snapshot and generate named materialisations with explicit fidelity and derivation metadata. GeoParquet/Parquet and a manifest are mandatory portable outputs; databases and indexes are rebuildable views.

## Consequences

- Flat files remain first-class.
- Format adapters can evolve independently.
- Storage duplication is acceptable when derivation is explicit.
- LanceDB is restricted to derived semantic/vector indexes.
