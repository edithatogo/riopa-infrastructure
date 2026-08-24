# Connector adapter authoring guide (bounded contract)

This guide describes the repository contract for adapters that turn an
approved source request into content-addressed capture evidence. It is a
repository implementation guide, not a source-rights decision, live-source
qualification, preservation certification, or release approval.

## Adapter lifecycle

1. Validate the request shape before network I/O. Use HTTPS, an explicit
   allow-list, no URL userinfo, bounded page/response sizes, and explicit
   source and endpoint identifiers.
2. Delegate transport to `HttpCaptureClient`. It records exact response bytes,
   redacted request/response metadata, status, timing, and SHA-256 identity.
3. Preserve failed attempts. Use `capture_with_retry` only for idempotent
   methods, with a bounded `RetryPolicy`, `CircuitBreaker`, and injected
   `RateLimiter`.
4. Reconcile completeness at the adapter boundary. Pagination must be stable;
   counts, object identities, declared totals, or successor checkpoints must
   agree before a capture set is emitted.
5. Quarantine suspect captures with `quarantine_capture`. Quarantine records
   reference the original digest and never modify raw objects.
6. Emit source-health and capability-drift observations, then write a redacted
   diagnostic bundle when an operation needs investigation.

## Implemented adapter surfaces

| Surface | Module | Required invariant |
|---|---|---|
| ArcGIS REST feature layer | `riopa_provenance.arcgis` | Count reconciliation and deterministic object-ID/offset pagination |
| WFS 2.0.0 | `riopa_provenance.wfs` | Stable sort/identity and declared-total reconciliation |
| Koordinates export | `riopa_provenance.linz_export` | Job-state evidence, redirect host policy, and exact download capture |
| Offline WARC/WACZ packaging | `riopa_provenance.web_archive` | Packages only an already-verified capture; policy-disabled by default |

## Required tests

Each adapter needs positive, malformed-response, pagination, duplicate/identity,
redaction, size/policy, retry, and integrity tests. Use offline fixtures or
`httpx.MockTransport`; do not put live payloads, credentials, or caches in the
repository.

## Explicit boundaries

The current contract does not establish a national or council real-source
capture, source rights/publication permission, hosted alerting, preservation
deposit, external operator reproduction, external user workflows, or beta/RC/
stable release qualification. Those gates remain pending in the Conductor plan.
