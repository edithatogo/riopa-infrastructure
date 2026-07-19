# ADR-0008: Stable Contracts, Compatibility and Deprecation

- **Status:** Proposed for v0.2 ratification
- **Date:** 2026-07-19

## Context

A v1 label is meaningful only if users can rely on schemas, identifiers, CLI/API behaviour and immutable historical releases.

## Decision

Use semantic versioning separately for software, schemas, ontologies, datasets and research objects. v1 minor releases remain backward compatible and cannot add required fields or change existing semantics. Breaking changes require a new major version, migration tooling and a documented coexistence period.

## Consequences

Compatibility fixtures, upgrade/rollback tests and deprecation windows are release gates. Historical snapshots and event hashes never change in place.
