# Evidence index: New Zealand spatial source and authority registry

- **Track ID:** `nz_spatial_source_registry_20260718`
- **Status:** `specified`
- **Target release:** `0.4.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Operational`
- **Risk / priority:** `High` / `P0`
- **V1 critical:** `yes`
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Spatial data lead
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/39

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| `WP-004-catalogue-disposition-pipeline-20260731` | Plan-bound catalogue scope flows through content-bound detail, service and planning stages | `src/riopa_provenance/linz_catalog.py`, `src/riopa_provenance/linz_enrichment.py`, `src/riopa_provenance/linz_inventory.py`, `src/riopa_provenance/linz_pipeline.py`, `tests/test_linz_pipeline.py` | Deterministic synthetic orchestration tests pass; no live catalogue claim |

## Blocking defects

- None recorded.

## Decisions, exceptions and limitations

- None recorded.

## Review and handover

Required agent-panel lenses: Governance analyst, API/schema analyst, Data-governance analyst, Operations analyst.

This index is deliberately non-assertive while the track remains `specified`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, agent-panel qualified where required, and sufficient for the applicable release gates.
