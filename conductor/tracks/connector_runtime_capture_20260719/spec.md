# Track: Common connector runtime and faithful capture framework

Track ID: `connector_runtime_capture_20260719`  
Phase: **Core**  
Target release: **0.4.0**  
Maturity target: **M6**  
Stability class: **Platform**  
V1 critical: **yes**

## Goal

Provide a reusable, secure and observable connector runtime that preserves exact acquisition evidence while keeping source-specific access logic modular.

## v1 role

This track is part of the stable v1 release contract. It is complete only when its implementation, compatibility, quality, security/governance, operational and reproducibility evidence satisfy both this specification and every applicable blocking gate in `conductor/releases.json` and `conductor/v1-gate.json`.

## Dependencies


- `provenance_profile_v1_20260718`
- `security_supply_chain_20260719`

## Scope

- Adapter protocol for APIs, ArcGIS, WFS/OGC, Koordinates, files, documents and web captures.
- HTTP request/response, headers, parameters, pagination, ETag, timestamps and service-version evidence.
- Immutable raw object storage, content addressing, resumability, retries and idempotency.
- Rate limits, authentication, robots/terms, secret handling and rights review hooks.
- Synthetic/public fixtures, health checks, observability and capability snapshots.

## Out of scope

- Embedding source-specific canonical transformation logic in the runtime.
- Bypassing authentication, access controls or source terms.

## Requirements

- **R01.** Raw bytes and metadata are persisted before a successful capture event is emitted.
- **R02.** Retries never duplicate logical captures without explicit attempt identity.
- **R03.** Secrets are injected at runtime and never recorded in provenance or fixtures.
- **R04.** Source capability and terms snapshots are versioned alongside captures.
- **R05.** Adapters can be tested offline against faithful public or synthetic fixtures.

## Acceptance criteria

- [ ] A common adapter interface supports at least ArcGIS REST, WFS/OGC, Koordinates/API, document download and web-archive capture classes.
- [ ] Captures record method, URL template, safe parameters, relevant headers, status, pagination, timing, bytes, digest, ETag and source/service identity.
- [ ] Retry, resume, idempotency, throttling, malformed response and partial failure tests pass.
- [ ] Rights/governance and authentication policies can block acquisition or publication independently.
- [ ] Source health and schema/capability drift generate actionable events and alerts.
- [ ] At least one real national and one council source complete the capture contract.

## Hardening and maturity gates

- M2 requires executable proof, negative tests and traceable evidence; interfaces may remain experimental.
- M3 requires real-data integration, migration evidence and representative failure handling.
- M4 requires repeated operation, external use, SLO evidence and bounded compatibility changes.
- M5 requires frozen interfaces, orchestrated agent-panel qualification, security/performance/recovery qualification and release-candidate soak.
- M6 requires supported compatibility, signed and preserved releases, external reproduction, named maintainers and post-release verification.
- Exceptions must be machine-readable, scoped, approved, time-limited and visible in release evidence.

## Evidence required

- Adapter protocol and conformance fixtures.
- Real capture event/raw-object examples.
- Retry, drift, security and rights negative tests.
- Connector health and performance report.

## Risks

- Common abstractions erase source-specific evidence.
- Raw capture unintentionally stores credentials or personal information.
- Retries overload fragile council services.
- Web capture violates terms or creates redistribution risk.

## Completion rule

The track may enter `complete` only after every acceptance criterion is evidenced in `index.md`, all blocking dependencies are complete, required migrations and documentation are published, and the target release readiness evaluator reports no track-specific blocker.
