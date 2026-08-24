# Evidence index: Supermarket access, zoning and health-geography reference study

- **Track ID:** `supermarket_health_pilot_20260718`
- **Status:** `active`
- **Target release:** `0.8.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Reference`
- **Risk / priority:** `High` / `P1`
- **V1 critical:** `yes`
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Research lead
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/109

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| `WP-010-non-operational-pilot-envelope-20260731` | Reference pilot outputs explicitly reject clinical, legal, commercial and live-operational suitability | `src/riopa_provenance/analysis.py`, `tests/test_analysis.py`, `reports/wp010-synthetic-methods-core.md` | Non-operational envelope passes on synthetic inputs; no supermarket dataset, reproduction or empirical health finding is claimed |
| `WP-010-public-source-intake-20260801` | Candidate population and supermarket sources retain explicit rights and acquisition state | `config/source-registry/wp010-public-pilot-candidates.yaml`, `tests/test_wp010_benchmark.py` | Population metadata is staged; supermarket acquisition remains rights-blocked and no empirical pilot is claimed |
| `WP-010-osm-regional-observation-20260801` | A bounded OSM sensitivity source is captured locally without being treated as authoritative | `scripts/capture_wp010_public_sources.py`, `tests/test_wp010_public_sources.py`, `reports/wp010-synthetic-methods-core.md` | Nine regional supermarket POIs observed; raw geometry remains local and completeness is not claimed |
| `SUPERMARKET-PREREGISTRATION-20260825` | Reference-only baseline estimands, geography, population, exclusions and discrepancy handling | `docs/supermarket-health-preregistration-20260825.json`, `tests/test_supermarket_preregistration.py` | Synthetic/non-clinical template validates; no supermarket dataset, empirical health finding, causal claim or external reproduction is enabled |

## Blocking defects

- Rights-cleared versioned supermarket inputs, baseline reproduction, access/health analysis,
  planning alternatives, research objects and orchestrated agent-panel qualification remain open.

## Decisions, exceptions and limitations

- Synthetic contract evidence is not a supermarket pilot result.

## Review and handover

Required agent-panel lenses: Data-governance analyst, Research-object analyst, Quantitative methods analyst, Scientific-methods analyst.

This index is deliberately non-assertive while the track remains `active` at M1. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, agent-panel qualified where required, and sufficient for the applicable release gates.
