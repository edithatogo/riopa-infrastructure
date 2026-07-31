# LINZ archive pipeline

The LINZ archive is executed as six content-bound stages:

1. catalogue enumeration;
2. item-detail capture;
3. service-inventory capture;
4. archive planning;
5. rights- and budget-approved payload capture; and
6. federation staging.

Details, services, and payload work use deterministic shards. Planning waits for
every detail and service shard, while federation waits for every payload shard.
`ready_linz_jobs` exposes only jobs whose dependencies have verified receipts,
which is suitable for constructing a GitHub Actions matrix without allowing a
later stage to race ahead.

Every job operation key binds the archive-plan hash, catalogue-items hash,
stage, shard, and shard count. Receipts bind the operation key and exact input
and output hashes. Identical receipt replay is a no-op; conflicting replay fails
closed.

Each job has storage and egress ceilings. A receipt exceeding either ceiling is
rejected and cannot advance the pipeline. Unknown-size and individually
oversized payloads remain isolated by the backfill planner for explicit review.

Changeset-derived layers are periodically checked against an independent full
export at the exact current revision. Reconciliation compares canonical table
semantics in primary-key order. A mismatch produces a content-bound `diverged`
report rather than advancing or rewriting the checkpoint.

These contracts and synthetic tests do not demonstrate live LINZ capture,
national-scale performance, scheduled operation, source rights approval, or a
completed external publication.
