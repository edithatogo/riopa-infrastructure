# Evidence index: Spatial quality, temporality and change-analysis framework

- **Track ID:** `spatial_quality_temporality_20260718`
- **Status:** `specified`
- **Target release:** `0.7.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Reference`
- **Risk / priority:** `High` / `P1`
- **V1 critical:** `yes`
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Spatial data lead
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/89

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| `WP-005-feature-differences-20260731` | Added, removed, attribute, exact-geometry, tolerance-geometry and schema differences | `src/riopa_provenance/spatial.py`, `tests/test_spatial.py`, `docs/change-and-impact-queries.md` | Synthetic deterministic fixtures pass; real historical and boundary-concordance evidence remains open |

## Blocking defects

- None recorded.

## Decisions, exceptions and limitations

- None recorded.

## Review and handover

Required agent-panel lenses: Provenance analyst, Data-governance analyst, Quantitative methods analyst, Scientific-methods analyst.

This index is deliberately non-assertive while the track remains `specified`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, agent-panel qualified where required, and sufficient for the applicable release gates.
