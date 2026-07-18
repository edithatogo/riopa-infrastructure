# ADR-0006: Standards Profile Rather Than a New Universal Standard

- **Status:** Accepted for v0.1
- **Date:** 2026-07-18

## Context

PROV, OpenLineage, RO-Crate, SLSA, DataCite, DCAT, Croissant, GeoParquet and STAC overlap but solve different problems. Implementing each independently would duplicate data and create inconsistent claims.

## Decision

Maintain a small native contract and normative mappings to pinned external standards. The release reports mapping loss and `conformsTo` versions.

## Consequences

- Adapters and conformance fixtures are part of the core product.
- External standards can evolve without rewriting historical events.
- RIOPA avoids claiming to replace mature community standards.
