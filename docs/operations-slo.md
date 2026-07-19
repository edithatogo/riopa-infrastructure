# Operations and service-level objectives

RIOPA SLOs describe managed infrastructure behaviour; they do not promise availability or correctness of upstream authorities.

## Stable indicators

- scheduled capture completion and idempotency;
- source-specific freshness and stale-source disposition;
- release-pipeline success and prevention of partial publication;
- quality-threshold compliance, exception age and quarantine backlog;
- preservation fixity, replica health and restore verification;
- alert acknowledgement, incident review and corrective-action closure;
- deterministic or tolerance-equivalent rebuild compliance;
- latency, throughput, resource, storage and third-party cost budgets.

## Exclusions

Upstream outage, approved maintenance and blocked rights/governance states may be excluded only when separately counted, explained and included in coverage reporting. Exclusions must not make stale, missing or legally uncertain data appear healthy.

## Stable qualification period

Before the 0.9.0 release candidate, operational components must provide at least **90 consecutive days** of representative beta evidence and at least three complete operating cycles, including a source or dependency failure, backfill and recovery. The exact candidate then completes at least **30 days** of soak.

The release record includes SLO calculations, raw observations, exclusions, incidents, restore evidence, cost/capacity evidence and unresolved operational risk. Targets remain candidate requirements until measured evidence is published; they are never presented as current achievements by the roadmap alone.
