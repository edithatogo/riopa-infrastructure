# Evidence index: New Zealand Spatial Archive real-data vertical slice

- **Track ID:** `nz_spatial_archive_mvp_20260718`
- **Status:** `specified`
- **Target release:** `0.5.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Reference`
- **Risk / priority:** `Critical` / `P0`
- **V1 critical:** `yes`
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Spatial data lead
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/49

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| `WP-004-sharded-archive-contract-20260731` | Catalogue-to-federation stages are independently resumable and content-bound | `src/riopa_provenance/linz_pipeline.py`, `tests/test_linz_pipeline.py`, `docs/linz-archive-pipeline.md` | Synthetic stage/dependency/replay tests pass; real-data MVP remains open |
| `WP-007-bounded-real-slice-20260731` | Real LINZ metadata, one WCC planning polygon, official planning PDF and facility CSV are content-addressed and linked to portable spatial materialisations | `evidence/wp007-real-slice/manifest.json`, `scripts/verify_wp007_slice.py`, `reports/wp007-bounded-real-slice.md` | Clean semantic rebuild passes; four-council/two-national-family coverage and external research-object validation remain open |

## Blocking defects

- None recorded.

## Decisions, exceptions and limitations

- None recorded.

## Review and handover

Required agent-panel lenses: Provenance analyst, Data-governance analyst, Operations analyst, Research-object analyst.

This index is deliberately non-assertive while the track remains `specified`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, agent-panel qualified where required, and sufficient for the applicable release gates.
