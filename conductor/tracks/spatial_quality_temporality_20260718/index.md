# Evidence index: Spatial quality, temporality and change-analysis framework

- **Track ID:** `spatial_quality_temporality_20260718`
- **Status:** `active`
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
| `SPATIAL-QUALITY-INPUT-HARDENING-20260829` | Reject non-object quality reports and profiles with controlled validation errors | `src/riopa_provenance/spatial_quality.py`, `tests/test_spatial_quality.py`, `docs/spatial-quality-input-hardening-20260829.json` | Negative input tests pass; heterogeneous real-council and national gates remain open |
| `SPATIAL-QUALITY-EVALUATOR-20260825` | Fail-closed evaluation of profile metrics with lineage, transformation and rights prerequisites | `src/riopa_provenance/spatial_quality.py`, `tests/test_spatial_quality.py` | Synthetic evaluator tests pass; real-council, historical/boundary and national completeness gates remain open |
| `SPATIAL-QUALITY-TREND-20260825` | Release-to-release trend and regression report contract with explicit tolerances | `src/riopa_provenance/spatial_quality_trend.py`, `tests/test_spatial_quality_trend.py`, `docs/spatial-quality-trend-report-20260825.json` | Repository contract passes on synthetic evaluations; heterogeneous real-council, national, external, elapsed and authority gates remain open |
| `SPATIAL-TEMPORAL-QUERY-20260825` | Explicit bitemporal transition validation and valid/recorded/as-known-at query contract | `src/riopa_provenance/transitions.py`, `tests/test_transitions.py`, `docs/spatial-temporal-query-contract-20260825.json`, `tests/test_spatial_temporal_query_contract.py` | Synthetic contract passes; real authority histories, late evidence, external semantics and publication gates remain open |
| `SPATIAL-QUALITY-CHANGE-ATTRIBUTION-20260825` | Declared revision-axis attribution with explicit ambiguity and missingness | `src/riopa_provenance/spatial_quality_trend.py`, `tests/test_spatial_quality_trend.py`, `docs/spatial-quality-change-attribution-contract-20260825.json` | Repository contract passes; causal provenance, real release histories, external qualification and authority remain open |
| `SPATIAL-TEMPORAL-HISTORY-AUDIT-20260825` | Declared late evidence, correction, supersession, finite-gap and overlapping-window audit | `src/riopa_provenance/transitions.py`, `tests/test_transitions.py`, `docs/spatial-temporal-history-audit-contract-20260825.json` | Bounded audit passes and retains overlap findings for adjudication; real historical coverage, authority, external qualification and publication remain open |
| `SPATIAL-SENSITIVITY-20260824` | Bounded sensitivity summary across declared boundary and denominator revisions | `src/riopa_provenance/spatial_sensitivity.py`, `tests/test_spatial_sensitivity.py`, `docs/spatial-sensitivity-contract-20260824.json` | All supplied observations are retained and promotion is disabled; real MAUP, denominator provenance, authority and national qualification remain open |
| `SPATIAL-BOUNDARY-CROSSWALK-20260825` | Revision-aware boundary crosswalk and population interpolation contract | `src/riopa_provenance/spatial_crosswalk.py`, `tests/test_spatial_crosswalk.py`, `docs/spatial-boundary-crosswalk-contract-20260825.json` | Local weighted projection passes; MAUP, denominator-version, real-boundary, national, external and authority gates remain open |
| `SPATIAL-QUALITY-UNCERTAINTY-PROPAGATION-20260825` | Declared spatial/temporal error propagation to a downstream uncertainty envelope | `src/riopa_provenance/spatial_quality_trend.py:propagate_spatial_temporal_uncertainty`, `tests/test_spatial_quality_trend.py` | Deterministic conditional envelope passes; sensitivities must be supplied and no authority, causal or operational claim is made |
| `SPATIAL-QUALITY-CLOSEOUT-EVIDENCE-20260825` | Link implementation, tests, review, migration and release-candidate evidence for the bounded quality slice | `docs/spatial-quality-closeout-evidence-20260825.json`, `tests/test_spatial_quality_closeout_evidence.py` | Evidence categories are linked and fail-closed; real-council, national, external and authority gates remain open |

The same revision’s Conductor regeneration receipt records the methods hash,
roadmap status, generated issue graph and full quality harness. This closes only
the bookkeeping task; national, authoritative, operational, external and release
gates remain open (`docs/spatial-quality-conductor-regeneration-20260825.json`).

| `SPATIAL-QUALITY-WAIVER-GOVERNANCE-20260825` | Expiry-checked quality waiver contract that cannot waive release-blocking metrics | `src/riopa_provenance/spatial_quality.py:evaluate_quality_waiver`, `docs/spatial-quality-waiver-governance-contract-20260825.json`, `tests/test_spatial_quality.py` | Bounded governance checks pass; real-council, national, authority and release qualification remain open |

| `SPATIAL-QUALITY-BENCHMARK-REPORT-20260825` | Deterministic benchmark summary over supplied spatial-quality observations | `src/riopa_provenance/spatial_quality.py:build_quality_benchmark_report`, `docs/spatial-quality-benchmark-report-contract-20260825.json`, `tests/test_spatial_quality.py` | Bounded report ordering and summaries pass; real-council, national and release qualification remain open |

## Blocking defects

- Heterogeneous real-council, historical/boundary and national completeness evidence remain open.
- MAUP qualification, external semantics and stable-release evidence remain open.

The 2026-08-25 closeout packet links the bounded profile, evaluator, trend,
temporal, crosswalk, sensitivity and uncertainty evidence. It does not
establish heterogeneous real-council validation, national completeness, MAUP
qualification, external semantics or a stable release.

## Decisions, exceptions and limitations

- None recorded.

## Review and handover

Required agent-panel lenses: Provenance analyst, Data-governance analyst, Quantitative methods analyst, Scientific-methods analyst.

This index is deliberately non-assertive while the track remains `active`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, agent-panel qualified where required, and sufficient for the applicable release gates.
