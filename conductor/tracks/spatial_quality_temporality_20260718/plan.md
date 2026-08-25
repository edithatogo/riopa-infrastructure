# Plan: spatial_quality_temporality_20260718

## 1. Quality profiles and ratchets

- [x] 1.1 Define profile-specific metrics, thresholds, warnings and waivers for the bounded regional public-preview profile. Geometry validity, repair, null geometry, stable identity, lineage and rights boundaries are machine-readable; real-council and national qualification remain open (`docs/spatial-quality-profile-contract-20260825.json`, `tests/test_spatial_quality_profile_contract.py`).
- [x] 1.2 Implement geometry, topology, completeness, uniqueness and rights checks.
- [x] 1.3 Add release-to-release quality trend and regression reports with explicit tolerances and fail-closed metric matching (`src/riopa_provenance/spatial_quality_trend.py`, `tests/test_spatial_quality_trend.py`, `docs/spatial-quality-trend-report-20260825.json`). Heterogeneous real-council, national, external, elapsed and authority gates remain open.

## 2. Temporal and change engine

- [x] 2.1 Implement explicit valid-time, recorded-time and `as_known_at` selection with fail-closed transition validation (`src/riopa_provenance/transitions.py`, `tests/test_transitions.py`, `docs/spatial-temporal-query-contract-20260825.json`, `tests/test_spatial_temporal_query_contract.py`). Real authority histories, late evidence, external semantics and publication gates remain open.
- [x] 2.2 Distinguish source, transformation, schema and boundary-induced changes using declared revision axes; multiple or missing axes remain ambiguous/insufficient. Real release-to-release attribution remains open (`src/riopa_provenance/spatial_quality_trend.py`, `tests/test_spatial_quality_trend.py`, `docs/spatial-quality-change-attribution-contract-20260825.json`).
- [x] 2.3 Audit declared late evidence, correction, supersession, finite historical gaps and overlapping windows with fail-closed invalid-record retention. Real historical source coverage and authority remain open (`src/riopa_provenance/transitions.py`, `tests/test_transitions.py`, `docs/spatial-temporal-history-audit-contract-20260825.json`).

## 3. Concordance and uncertainty

- [x] 3.1 Implement revision-aware boundary crosswalk and population interpolation contracts with fail-closed weight and coverage checks. MAUP, denominator-version, real-boundary and authority qualification remain open (`src/riopa_provenance/spatial_crosswalk.py`, `tests/test_spatial_crosswalk.py`, `docs/spatial-boundary-crosswalk-contract-20260825.json`).
- [x] 3.2 Add bounded boundary/denominator revision sensitivity analysis with fail-closed estimates and explicit non-claims. Real MAUP, denominator provenance and authority qualification remain open. (`src/riopa_provenance/spatial_sensitivity.py`, `tests/test_spatial_sensitivity.py`, `docs/spatial-sensitivity-contract-20260824.json`; commit `a0f2d76`)
- [x] 3.3 Propagate spatial/temporal uncertainty to downstream interfaces. Evidence: `propagate_spatial_temporal_uncertainty` returns a declared-sensitivity interval with spatial/temporal components, explicit inputs and promotion disabled; tests cover deterministic output and fail-closed negatives.

## 4. Agent-panel quality validation

- [ ] 4.1 Validate profiles on heterogeneous real council layers.
- [x] 4.2 Review blocking thresholds and waiver governance. The bounded expiry-checked waiver evaluator requires owner/rationale evidence and rejects expired or release-blocking waivers; real-council and release-authority review remains open (`src/riopa_provenance/spatial_quality.py:evaluate_quality_waiver`, `docs/spatial-quality-waiver-governance-contract-20260825.json`).
- [x] 4.3 Generate deterministic bounded quality benchmark reports from supplied observations. Reports preserve profile/revision/rights context and remain promotion-disabled; real-council, national and release qualification remain open (`src/riopa_provenance/spatial_quality.py:build_quality_benchmark_report`, `docs/spatial-quality-benchmark-report-contract-20260825.json`).

## Track closeout

- [x] C.1 Link implementation, test, review, migration and release evidence in `index.md` for the repository-owned closeout slice; real-council, national, external and authority gates remain explicitly pending (`docs/spatial-quality-closeout-evidence-20260825.json`, `tests/test_spatial_quality_closeout_evidence.py`; `f6c99da`).
- [x] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected. The locked methods generation, roadmap status, issue graph and full quality harness passed; the methods output was temporary and not a release artifact (`docs/spatial-quality-conductor-regeneration-20260825.json`).
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [x] C.4 Update metadata status and target-release evidence through the Conductor workflow; metadata is `active`/M1 for target release `0.7.0`, with real-council, national, external and authority gates unresolved.

## Review fixes

- [x] R1 Register the new spatial-sensitivity module in the Python 3.14 coverage inventory after CI discovery. (`docs/module-coverage-inventory-20260825.json`; commit `cd0bd72`)
