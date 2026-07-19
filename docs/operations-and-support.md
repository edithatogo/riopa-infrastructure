# Operations, preservation and support model

Stable v1 is a maintained research infrastructure release, not merely a source-code snapshot.

## Operational controls

- Per-source update schedule, owner, freshness objective, load limit, rights status and backfill boundary.
- Structured capture, transformation, quality, source-health and release events.
- Idempotent retries, bounded queues, quarantine, partial-release handling and explicit manual review.
- Monitoring for source disappearance, capability/schema drift, geometry/identity change, stale outputs and preservation fixity.
- Correction, supersession, withdrawal and source-retirement workflows that preserve historical evidence.

## Reliability evidence

M3 requires repeated operational cycles. M4 requires exercised restore, rollback, correction and withdrawal. M5 requires release-candidate soak and capacity qualification. M6 requires stable SLO evidence, disaster recovery, preservation restoration, named operational ownership and acceptable cost/capacity risk.

## Support boundaries

The stable release identifies supported software environments, file formats, profile versions and reference workflows. Support covers documented behaviour within those boundaries. It does not certify planning law, clinical safety, live emergency dispatch, commercial viability or causal health effects.

## Sustainability

The maintainer roster, triage rules, security response, release cadence, deprecation windows, storage/compute budgets and succession plan are reviewed at least annually. Unsupported capabilities remain clearly labelled experimental or archived.
