# Track: Spatial quality, temporality and change-analysis framework

Track ID: `spatial_quality_temporality_20260718`  
Phase: **NZ Spatial**  
Target release: **0.7.0**  
Maturity target: **M6**  
Stability class: **Reference**  
V1 critical: **yes**

## Goal

Make geometry, topology, completeness, positional, temporal and semantic quality measurable and support defensible historical, boundary and change analyses.

## v1 role

This track is part of the stable v1 release contract. It is complete only when its implementation, compatibility, quality, security/governance, operational and reproducibility evidence satisfy both this specification and every applicable blocking gate in `conductor/releases.json` and `conductor/v1-gate.json`.

## Dependencies


- `nz_spatial_archive_mvp_20260718`
- `planning_rules_linkage_20260718`
- `provenance_query_api_20260719`

## Scope

- Quality profiles, thresholds, warnings, waivers and trend ratchets.
- Geometry validity, topology, completeness, positional and semantic checks.
- Bitemporal query, change-set, reconstruction and uncertainty handling.
- Boundary concordance, population interpolation, MAUP and denominator versioning.
- Quality-aware downstream contracts for access, facility and health analyses.

## Out of scope

- One universal accuracy threshold for every source and use case.
- Repairing or imputing uncertain geometry/time without retaining the original evidence.

## Requirements

- **R01.** Quality is profile- and use-case-specific but comparable across releases.
- **R02.** Blocking thresholds and waivers are machine readable and time limited.
- **R03.** Original and repaired geometry are separately identifiable.
- **R04.** Change detection distinguishes source change, transformation change and boundary concordance artifacts.
- **R05.** Area-based outcomes retain denominator and boundary versions.

## Acceptance criteria

- [ ] Quality profiles cover completeness, validity, consistency, positional/temporal accuracy, uniqueness, lineage, rights and accessibility where applicable.
- [ ] Geometry and topology tests identify and quantify repair effects.
- [ ] Bitemporal change queries pass synthetic and real historical fixtures.
- [ ] Boundary concordance and MAUP sensitivity are available for area-level analyses.
- [ ] Quality thresholds block unsuitable downstream analyses or require explicit waiver.
- [ ] Release-to-release quality trends and unresolved regressions are published.

## Hardening and maturity gates

- M2 requires executable proof, negative tests and traceable evidence; interfaces may remain experimental.
- M3 requires real-data integration, migration evidence and representative failure handling.
- M4 requires repeated operation, external use, SLO evidence and bounded compatibility changes.
- M5 requires frozen interfaces, independent review, security/performance/recovery qualification and release-candidate soak.
- M6 requires supported compatibility, signed and preserved releases, external reproduction, named maintainers and post-release verification.
- Exceptions must be machine-readable, scoped, approved, time-limited and visible in release evidence.

## Evidence required

- Quality profiles, threshold policies and waiver records.
- Geometry/topology repair-effect reports.
- Temporal/change and concordance validation fixtures.
- Quality trend and downstream suitability reports.

## Risks

- Quality scores conceal dimension-specific failures.
- Geometry repair changes substantive boundaries.
- Boundary concordance introduces unreported uncertainty.
- Historical source gaps are mistaken for no change.

## Completion rule

The track may enter `complete` only after every acceptance criterion is evidenced in `index.md`, all blocking dependencies are complete, required migrations and documentation are published, and the target release readiness evaluator reports no track-specific blocker.
