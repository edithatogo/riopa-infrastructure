# ADR-0001: Federated Repository Ecosystem

- **Status:** Accepted for v0.1
- **Date:** 2026-07-18

## Context

Existing connectors, archives, corpora and analytical packages have useful, domain-specific boundaries. A monorepo would simplify initial coordination but create coupling, duplicate release cycles and discourage independent reuse.

## Decision

Use a federated ecosystem with shared contracts. Keep the initial reference implementation and profile tooling together until stable package boundaries are demonstrated. Extract packages when at least two repositories consume the same interface.

## Consequences

- Cross-repo compatibility tests and version policy are required.
- Conductor tracks and GitHub projects must expose dependencies across repositories.
- No repository is required to adopt irrelevant components.
- The architecture tolerates Python, Rust and other implementations.
