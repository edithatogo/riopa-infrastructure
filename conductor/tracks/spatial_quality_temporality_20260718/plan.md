# Plan: spatial_quality_temporality_20260718

## 1. Quality profiles and ratchets

- [~] 1.1 Define profile-specific metrics, thresholds, warnings and waivers for the bounded regional public-preview profile. Geometry validity, repair, null geometry, stable identity, lineage and rights boundaries are machine-readable; real-council and national qualification remain open (`docs/spatial-quality-profile-contract-20260825.json`, `tests/test_spatial_quality_profile_contract.py`).
- [x] 1.2 Implement geometry, topology, completeness, uniqueness and rights checks.
- [x] 1.3 Add release-to-release quality trend and regression reports with explicit tolerances and fail-closed metric matching (`src/riopa_provenance/spatial_quality_trend.py`, `tests/test_spatial_quality_trend.py`, `docs/spatial-quality-trend-report-20260825.json`). Heterogeneous real-council, national, external, elapsed and authority gates remain open.

## 2. Temporal and change engine

- [x] 2.1 Implement explicit valid-time, recorded-time and `as_known_at` selection with fail-closed transition validation (`src/riopa_provenance/transitions.py`, `tests/test_transitions.py`, `docs/spatial-temporal-query-contract-20260825.json`, `tests/test_spatial_temporal_query_contract.py`). Real authority histories, late evidence, external semantics and publication gates remain open.
- [~] 2.2 Distinguish source, transformation, schema and boundary-induced changes using declared revision axes; multiple or missing axes remain ambiguous/insufficient (`src/riopa_provenance/spatial_quality_trend.py`, `tests/test_spatial_quality_trend.py`, `docs/spatial-quality-change-attribution-contract-20260825.json`). Real release-to-release attribution remains open.
- [x] 2.3 Audit declared late evidence, correction, supersession, finite historical gaps and overlapping windows with fail-closed invalid-record retention. Real historical source coverage and authority remain open (`src/riopa_provenance/transitions.py`, `tests/test_transitions.py`, `docs/spatial-temporal-history-audit-contract-20260825.json`).

## 3. Concordance and uncertainty

- [~] 3.1 Implement revision-aware boundary crosswalk and population interpolation contracts with fail-closed weight and coverage checks. MAUP, denominator-version, real-boundary and authority qualification remain open (`src/riopa_provenance/spatial_crosswalk.py`, `tests/test_spatial_crosswalk.py`, `docs/spatial-boundary-crosswalk-contract-20260825.json`).
- [ ] 3.2 Add MAUP and denominator-version sensitivity analyses.
- [ ] 3.3 Propagate spatial/temporal uncertainty to downstream interfaces.

## 4. Agent-panel quality validation

- [ ] 4.1 Validate profiles on heterogeneous real council layers.
- [ ] 4.2 Review blocking thresholds and waiver governance.
- [ ] 4.3 Publish quality framework and benchmark reports.

## Track closeout

- [ ] C.1 Link implementation, test, review, migration and release evidence in `index.md`.
- [ ] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [ ] C.4 Update metadata status and target-release evidence through the Conductor workflow.
