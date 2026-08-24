# Plan: spatial_quality_temporality_20260718

## 1. Quality profiles and ratchets

- [~] 1.1 Define profile-specific metrics, thresholds, warnings and waivers for the bounded regional public-preview profile. Geometry validity, repair, null geometry, stable identity, lineage and rights boundaries are machine-readable; real-council and national qualification remain open (`docs/spatial-quality-profile-contract-20260825.json`, `tests/test_spatial_quality_profile_contract.py`).
- [x] 1.2 Implement geometry, topology, completeness, uniqueness and rights checks.
- [x] 1.3 Add release-to-release quality trend and regression reports with explicit tolerances and fail-closed metric matching (`src/riopa_provenance/spatial_quality_trend.py`, `tests/test_spatial_quality_trend.py`, `docs/spatial-quality-trend-report-20260825.json`). Heterogeneous real-council, national, external, elapsed and authority gates remain open.

## 2. Temporal and change engine

- [ ] 2.1 Implement valid-time, recorded-time and reconstruction query primitives.
- [ ] 2.2 Distinguish source, transformation, schema and boundary-induced changes.
- [ ] 2.3 Test late evidence, correction, supersession and historical gaps.

## 3. Concordance and uncertainty

- [ ] 3.1 Implement boundary crosswalk and population interpolation contracts.
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
