# Evidence index: National archive coverage, updates and operations

- **Track ID:** `nz_spatial_archive_operations_20260719`
- **Status:** `active`
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
| `NZ-SPATIAL-ROLLOUT-PLAN-20260825` | Prioritised source waves, bounded schedules/load limits, exception review and retirement workflow | `docs/nz-spatial-archive-rollout-plan-20260825.json`, `tests/test_nz_spatial_rollout_plan.py` | Repository-owned planning contract passes; no live capture, national coverage, preservation acceptance or beta SLO evidence is claimed |

## Blocking defects

- Live connector deployment, source rights/credential gates, beta SLO duration, national restore and accountable release approval remain open.

## Decisions, exceptions and limitations

- None recorded.

## Review and handover

Required agent-panel lenses: Governance analyst, Data-governance analyst, Operations analyst, Research-object analyst.

This index is deliberately non-assertive while the track remains `active` at M1. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, agent-panel qualified where required, and sufficient for the applicable release gates.
