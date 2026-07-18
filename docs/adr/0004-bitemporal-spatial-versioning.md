# ADR-0004: Bitemporal Versioning for Spatial and Legal State

- **Status:** Accepted for v0.1
- **Date:** 2026-07-18

## Context

Council layers can be published, edited, retrieved, notified, made operative and superseded at different times. A single `updated_at` field cannot support defensible historical analysis.

## Decision

Represent both valid/effective time and system/recorded time, with additional source publication, retrieval, operative and supersession assertions. Unknown legal times remain unknown and sourced confidence is recorded.

## Consequences

- Queries must state the temporal perspective used.
- Historical reconstruction can be distinguished from contemporaneous capture.
- More storage is required because entity versions are immutable.
