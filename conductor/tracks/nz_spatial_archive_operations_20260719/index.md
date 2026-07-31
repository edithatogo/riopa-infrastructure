# Evidence index: National archive coverage, updates and operations

- **Track ID:** `nz_spatial_archive_operations_20260719`
- **Status:** `specified`
- **Target release:** `0.8.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Operational`
- **Risk / priority:** `Critical` / `P0`
- **V1 critical:** `yes`
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Spatial data lead
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/119

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| `WP-004-resume-budget-reconcile-20260731` | Sharded retries, storage/egress bounds and periodic full-export reconciliation | `src/riopa_provenance/linz_pipeline.py`, `src/riopa_provenance/linz.py`, `tests/test_linz_pipeline.py`, `tests/test_linz.py` | Synthetic orchestration and semantic divergence tests pass; operational period remains open |

## Blocking defects

- None recorded.

## Decisions, exceptions and limitations

- None recorded.

## Review and handover

Required reviewer roles: Governance reviewer, Data steward, Operations reviewer, Research-object reviewer.

This index is deliberately non-assertive while the track remains `specified`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, independently reviewed where required, and sufficient for the applicable release gates.
