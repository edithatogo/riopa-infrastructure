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
| `SPATIAL-QUALITY-TREND-20260825` | Release-to-release trend and regression report contract with explicit tolerances | `src/riopa_provenance/spatial_quality_trend.py`, `tests/test_spatial_quality_trend.py`, `docs/spatial-quality-trend-report-20260825.json` | Repository contract passes on synthetic evaluations; heterogeneous real-council, national, external, elapsed and authority gates remain open |
| `SPATIAL-TEMPORAL-QUERY-20260825` | Explicit bitemporal transition validation and valid/recorded/as-known-at query contract | `src/riopa_provenance/transitions.py`, `tests/test_transitions.py`, `docs/spatial-temporal-query-contract-20260825.json`, `tests/test_spatial_temporal_query_contract.py` | Synthetic contract passes; real authority histories, late evidence, external semantics and publication gates remain open |
| `SPATIAL-QUALITY-CHANGE-ATTRIBUTION-20260825` | Declared revision-axis attribution with explicit ambiguity and missingness | `src/riopa_provenance/spatial_quality_trend.py`, `tests/test_spatial_quality_trend.py`, `docs/spatial-quality-change-attribution-contract-20260825.json` | Repository contract passes; causal provenance, real release histories, external qualification and authority remain open |
| `SPATIAL-TEMPORAL-HISTORY-AUDIT-20260825` | Declared late evidence, correction, supersession and finite-gap audit | `src/riopa_provenance/transitions.py`, `tests/test_transitions.py`, `docs/spatial-temporal-history-audit-contract-20260825.json` | Bounded audit passes; real historical coverage, authority, external qualification and publication remain open |
| `SPATIAL-BOUNDARY-CROSSWALK-20260825` | Revision-aware boundary crosswalk and population interpolation contract | `src/riopa_provenance/spatial_crosswalk.py`, `tests/test_spatial_crosswalk.py`, `docs/spatial-boundary-crosswalk-contract-20260825.json` | Local weighted projection passes; MAUP, denominator-version, real-boundary, national, external and authority gates remain open |

## Blocking defects

- None recorded.

## Decisions, exceptions and limitations

- None recorded.

## Review and handover

Required agent-panel lenses: Provenance analyst, Data-governance analyst, Quantitative methods analyst, Scientific-methods analyst.

This index is deliberately non-assertive while the track remains `specified`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, agent-panel qualified where required, and sufficient for the applicable release gates.
