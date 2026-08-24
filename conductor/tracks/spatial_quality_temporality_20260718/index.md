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
| `SPATIAL-QUALITY-PROFILE-20260825` | Bounded profile metrics, thresholds, warnings, waivers and required evidence | `docs/spatial-quality-profile-contract-20260825.json`, `tests/test_spatial_quality_profile_contract.py` | Repository contract is validated; heterogeneous real-council, historical/boundary and national completeness gates remain open |
| `SPATIAL-QUALITY-EVALUATOR-20260825` | Fail-closed evaluation of profile metrics with lineage, transformation and rights prerequisites | `src/riopa_provenance/spatial_quality.py`, `tests/test_spatial_quality.py` | Synthetic evaluator tests pass; real-council, historical/boundary and national completeness gates remain open |

## Blocking defects

- None recorded.

## Decisions, exceptions and limitations

- None recorded.

## Review and handover

Required agent-panel lenses: Provenance analyst, Data-governance analyst, Quantitative methods analyst, Scientific-methods analyst.

This index is deliberately non-assertive while the track remains `specified`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, agent-panel qualified where required, and sufficient for the applicable release gates.
