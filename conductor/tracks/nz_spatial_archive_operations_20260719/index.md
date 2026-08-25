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
| `NZ-SPATIAL-ARCHIVE-OPERATIONS-CORE-20260825` | Delta decisions, drift quarantine, partial-release assembly and multidimensional reporting | `src/riopa_provenance/archive_operations.py`, `tests/test_archive_operations.py`, `docs/nz-spatial-archive-operations-contract-20260825.json`, `tests/test_nz_spatial_archive_operations_contract.py` | Repository-owned implementation and negative tests pass; decisions remain digest-only, reports remain bounded to supplied observations and promotion is prohibited |

The same revision’s Conductor regeneration receipt records the methods hash,
roadmap status, generated issue graph and full quality harness. This closes only
the bookkeeping task; hosted recovery, preservation, elapsed-soak, external
operation and authority gates remain open (`docs/nz-archive-operations-conductor-regeneration-20260825.json`).

## Blocking defects

- Blocking dependencies remain incomplete: `nz_spatial_archive_mvp_20260718`, `spatial_quality_temporality_20260718`, `operations_preservation_sre_20260719` and `nz_spatial_source_registry_20260718`.
- The complete current-authority inventory and source-specific rights, credentials and reviewed exceptions are unavailable.
- Live connector deployment, national observation/report generation, the beta SLO duration and operational exception resolution remain open.
- National-scale restore, correction, retirement, preservation, capacity and cost exercises have not occurred.
- Accountable stable-model approval, publication and target-release readiness remain open.

## Decisions, exceptions and limitations

- Repository-owned operations decisions are deliberately non-promotable. They bind supplied digests and dispositions but do not contact endpoints, preserve payload bytes, infer national completeness or replace accountable approval.
- A reconstructed backfill is rejected unless it carries an explicit reconstruction timestamp; it cannot silently appear to be a contemporaneous capture.

## Review and handover

Required agent-panel lenses: Governance analyst, Data-governance analyst, Operations analyst, Research-object analyst.

This index is deliberately non-assertive while the track remains `active` at M1. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, agent-panel qualified where required, and sufficient for the applicable release gates.
