# Feature change and provenance impact queries

RIOPA exposes two bounded, deterministic contracts for local comparison and
lineage analysis. Neither contract promotes a derived projection to archival
truth.

## Feature snapshot differences

`compare_feature_snapshots` compares normalized feature records using
`feature.id`, or an explicitly selected identity property. It reports:

- added and removed identities;
- attribute changes;
- exact geometry changes, using canonical WKB byte equality;
- geometry changes within and beyond an explicit Hausdorff-distance tolerance;
- properties added to or removed from the snapshot schema; and
- hashes binding the input snapshots and the resulting report.

Exact and tolerance results remain separate. A tolerance result therefore
cannot erase the evidence that coordinates changed. The function does not
infer whether a difference originated in a source, transformation, schema, or
boundary operation; that determination requires the associated capture and
transformation provenance.

## Where, why, how, and rebuild impact

`LineageIndex.query` answers:

- `where`: downstream products reachable from the selected node;
- `why`: upstream evidence reachable from the selected node; and
- `how`: direct, typed relations involving the selected node.

`LineageIndex.rebuild_impact` conservatively returns every reachable downstream
node for the supplied roots. Every response includes the authoritative
manifest identifiers and hashes, a hash of the disposable SQLite projection,
freshness explicitly scoped to that listed authoritative evidence set, the
granularities actually present, and an explicit limitation when feature or row
lineage was not captured.

## Projection reconciliation

Re-importing a manifest transactionally replaces its edges and removes nodes
that are no longer referenced by any authoritative manifest edge.
`LineageIndex.reconcile_projection` exposes the same deterministic orphan
policy for maintenance and returns the sorted identities removed. Shared nodes
and any node retained by at least one manifest edge are preserved.

These are synthetic/local contracts. They do not establish real-release query
conformance, graph equivalence, performance, access-control, or external-user
evidence required to close the related Conductor tracks.
