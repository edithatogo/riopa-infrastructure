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

## Blocking defects

- None recorded.

## Decisions, exceptions and limitations

- None recorded.

## Review and handover

Required reviewer roles: Provenance reviewer, Data steward, Operations reviewer, Research-object reviewer.

This index is deliberately non-assertive while the track remains `specified`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, independently reviewed where required, and sufficient for the applicable release gates.
