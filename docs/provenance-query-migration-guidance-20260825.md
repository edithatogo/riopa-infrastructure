# Provenance-query migration guidance (bounded local contract)

This guidance applies to the repository-owned local query contract. It is a
compatibility policy, not a v1 release freeze or a promise of MCP/remote
support.

## Current contract

`LineageQuery` version `1.0.0` contains `node_id`, `question` (`where`,
`why`, or `how`) and `max_depth` (1–100). Requests are evaluated against a
validated local projection. The projection fingerprint and authoritative
evidence envelope are part of the response.

## Additive changes

- Clients should ignore unknown response members.
- CLI pagination (`--page-size`, `--offset`) is an additive presentation
  feature; it does not change the underlying query semantics.
- Cache diagnostics are advisory and must not be used as evidence of source
  freshness beyond the listed projection fingerprint.

## Breaking changes

- Changing question meanings, node identity, depth bounds, answer ordering or
  evidence-envelope semantics requires a new major contract version.
- A projection fingerprint change invalidates cached answers; clients must
  treat the answer as newly evaluated.
- A missing or unverifiable authoritative manifest is a failed query, not
  negative evidence.

## Explicit boundaries

This document does not establish remote authorization, MCP transport,
production performance, real-user validation, external reproduction, release
approval or operational suitability. Those remain separate evidence gates.
