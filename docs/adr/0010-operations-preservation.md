# ADR-0010: Operations and Preservation Are Product Capabilities

- **Status:** Proposed for v0.2 ratification
- **Date:** 2026-07-19

## Context

A reproducible one-off pipeline can still fail as public infrastructure if source changes, retries, corrections, costs, restoration and long-term preservation are unmanaged.

## Decision

Treat schedules, SLOs, observability, runbooks, quarantine, backfill, correction, withdrawal, fixity, replicas and restore drills as first-class v1 capabilities. Stable dependencies require named operational ownership.

## Consequences

The archive must operate through representative update and failure cycles before GA. Unsupported experiments cannot become hidden production dependencies.
