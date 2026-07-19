# ADR-0009: Integrity, Authenticity and Software Supply-Chain Trust

- **Status:** Proposed for v0.2 ratification
- **Date:** 2026-07-19

## Context

Content hashes detect mutation but do not identify the producer or protect acquisition, CI and release workflows from compromise.

## Decision

Retain content-addressed evidence and add threat models, least-privilege automation, SBOMs, identity-bearing signed attestations, dependency controls and incident response. Trust claims remain scoped: a valid signature proves origin under a policy, not factual truth of source content.

## Consequences

Security evidence and verification policy become mandatory for stable releases. Critical vulnerabilities block GA.
