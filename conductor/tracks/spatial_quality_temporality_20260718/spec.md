# Track: Spatial quality, temporality and change-analysis framework

Track ID: `spatial_quality_temporality_20260718`  
Phase: **NZ Spatial**

## Goal

Make spatial, temporal and semantic quality measurable and support defensible historical/change analyses.

## Dependencies

- `nz_spatial_archive_mvp_20260718`
- `planning_rules_linkage_20260718`

## Scope

- ISO 19157-1/DQV-aligned metrics.
- Geometry validity, overlap/gap, positional and thematic checks.
- Bitemporal queries, snapshot diff and historical reconstruction labels.
- Boundary concordances and area/population weighting.
- Quality trend and source-freshness reports.

## Out of scope

- A single opaque quality score.
- Treating reconstructed history as contemporaneous observation.

## Acceptance criteria

- [ ] Every released layer has a declared quality profile and metric results.
- [ ] Spatial diffs separate schema, attribute and geometry changes.
- [ ] Queries can reproduce state as-known-at and state-valid-at perspectives.
- [ ] Boundary concordance uncertainty and aggregation method are recorded.
- [ ] Quality warnings flow into methods and analytical sensitivity analyses.

## Risks

- Metrics interpreted as ground truth.
- Topology checks inappropriate for some layers.
- Boundary change bias.
