# Track: Operations, service reliability and digital preservation

Track ID: `operations_preservation_sre_20260719`  
Phase: **Foundation**  
Target release: **0.8.0**  
Maturity target: **M6**  
Stability class: **Operational**  
V1 critical: **yes**

## Goal

Operate captures, transformations, releases and preservation as a measured service with observable health, explicit SLOs, fixity, recovery and sustainable cost controls.

## v1 role

This track is part of the stable v1 release contract. It is complete only when its implementation, compatibility, quality, security/governance, operational and reproducibility evidence satisfy both this specification and every applicable blocking gate in `conductor/releases.json` and `conductor/v1-gate.json`.

## Dependencies


- `foundation_architecture_20260718`
- `security_supply_chain_20260719`

## Scope

- Job scheduling, idempotency, retries, quarantine, partial failure and backpressure.
- Source-health, freshness, quality, storage, cost and release observability.
- Service-level indicators/objectives, incident severity, on-call and communication expectations.
- Retention, replicas, fixity audits, preservation packages, restore and disaster recovery.
- Correction, supersession, withdrawal and end-of-life operations.

## Out of scope

- Promising uptime for upstream council or national services.
- Treating a dashboard or database as the archival source of truth.

## Requirements

- **R01.** Scheduled work is safe to retry and records attempts, causal identity and outcomes.
- **R02.** Every source has a freshness expectation or an explicit unmanaged classification.
- **R03.** Every release has at least two independent preservation copies or documented exception.
- **R04.** Operational SLO calculations explain upstream exclusions and maintenance windows.
- **R05.** Recovery point and recovery time targets are tied to tested restore procedures.

## Acceptance criteria

- [ ] Operational SLIs and SLOs cover capture success, freshness, release success, fixity, alerting and restore readiness.
- [ ] The beta operates for at least ninety consecutive days with published SLO and incident evidence before v1 RC.
- [ ] Fixity audits, backup restore and full disaster-recovery exercises pass.
- [ ] Runbooks cover source outage, schema drift, rights change, corruption, compromised release, withdrawal and capacity exhaustion.
- [ ] Storage, compute and third-party-service costs have budgets, forecasts and alert thresholds.
- [ ] Stable releases have correction, supersession, retention and end-of-support procedures.

## Hardening and maturity gates

- M2 requires executable proof, negative tests and traceable evidence; interfaces may remain experimental.
- M3 requires real-data integration, migration evidence and representative failure handling.
- M4 requires repeated operation, external use, SLO evidence and bounded compatibility changes.
- M5 requires frozen interfaces, orchestrated agent-panel qualification, security/performance/recovery qualification and release-candidate soak.
- M6 requires supported compatibility, signed and preserved releases, external reproduction, named maintainers and post-release verification.
- Exceptions must be machine-readable, scoped, approved, time-limited and visible in release evidence.

## Evidence required

- SLO definitions and rolling reports.
- Operational dashboards, alerts and source-health records.
- Runbooks, incident logs and post-incident reviews.
- Fixity, restore, disaster-recovery and cost/capacity reports.

## Risks

- A nominal automated archive silently becomes stale.
- Upstream failures are hidden to make SLOs look healthy.
- Preservation copies share one failure domain.
- Backfills or large geometry jobs exhaust budget or capacity.

## Completion rule

The track may enter `complete` only after every acceptance criterion is evidenced in `index.md`, all blocking dependencies are complete, required migrations and documentation are published, and the target release readiness evaluator reports no track-specific blocker.
