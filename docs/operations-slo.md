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

Before the 0.9.0 release candidate, operational components must provide at least
**90 consecutive calendar days** with at least **90 daily hosted observations**
and three complete operating cycles, including an injected source or dependency
failure, backfill and recovery. The unchanged exact candidate then completes at
least **7 consecutive calendar days** with at least **7 daily hosted
observations**. A candidate revision change restarts its soak segment.

“Hosted” means a scheduled workflow actually ran outside the developer laptop
against an exact revision and emitted an immutable receipt. “Elapsed” means the
receipts span real calendar time; it is not command runtime and cannot be
simulated with future timestamps. An SLO is the measured target for the
repository-operated capture, freshness, release, fixity, restore and alerting
pipeline. Upstream failures and approved exclusions remain counted and visible.

The release record includes SLO calculations, raw observations, exclusions, incidents, restore evidence, cost/capacity evidence and unresolved operational risk. Targets remain candidate requirements until measured evidence is published; they are never presented as current achievements by the roadmap alone.
