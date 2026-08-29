# Evidence index: Versioned multi-source facility registry

- **Track ID:** `facility_registry_20260719`
- **Status:** `active`
- **Target release:** `0.6.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Reference`
- **Risk / priority:** `High` / `P1`
- **V1 critical:** `yes`
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Methods and analytics lead
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/59

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| `WP-007-public-hospital-source-20260731` | Official certified public-hospital provider CSV is preserved with content hash, HTTP receipt, rights reference and source limitation | `evidence/wp007-real-slice/manifest.json`, `reports/wp007-bounded-real-slice.md` | Real single-source capture passes; multi-source reconciliation, coordinates, history and review metrics remain open |
| `WP-010-bounded-reconciliation-20260801` | Independent assertions retain source identity, coordinates, rights and authority class; deterministic matching preserves conflicts and requires accountable review | `src/riopa_provenance/facility_registry.py`, `tests/test_facility_registry.py`, `scripts/compare_wp010_facility_sources.py`, `reports/wp010-facility-source-sensitivity.md` | Reference implementation and bounded council/OSM sensitivity pass locally; no candidate is adjudicated or promoted to authoritative status |
| `WP-010-bounded-pilot-decision-20260801` | Pilot scope, source exclusions and publication conditions are explicit | `docs/wp010-bounded-pilot-decision.md` | Approved for the bounded regional public-data pilot only; beta, RC and stable promotion remain excluded |
| `WP-010-preservation-manifest-20260801` | Exact revision, source hashes, reviewer bundle and exclusions are preserved | `evidence/wp010-bounded-pilot/manifest.json`, [Zenodo 10.5281/zenodo.21737563](https://doi.org/10.5281/zenodo.21737563) | Successor packet deposited with recorded SHA-256; this does not close isolated role-separated clean-room agent reproduction or higher-tier release gates |
| `WP-010-bounded-pilot-review-policy-20260801` | Pilot-level agent review is separated from beta/stable isolated role-separated clean-room agent reproduction | `docs/bounded-pilot-review-protocol.md`, `reports/wp010-subagent-review-20260801.md` | Pilot review may support bounded internal scope; role-separated agent-panel gate remains mandatory for higher promotion |
| `FACILITY-PUBLIC-SOURCE-ROUTING-20260802` | Missing public retail/health/ambulance inputs are separated from licensed sources and routed through archive-first acquisition | `docs/public-dataset-archive-incorporation-plan-20260802.json`, [open_social_data issue 36](https://github.com/edithatogo/open_social_data/issues/36), `tests/test_public_dataset_archive_plan.py` | Public food-retail acquisition issue remains open; authoritative ambulance coverage remains pending; Healthpoint payloads excluded |
| `FACILITY-PUBLIC-HEALTH-SOURCE-FAMILIES-20260825` | Two distinct public health source families have immutable archive evidence | `config/archive-sources/rangitikei-public-ambulance-2023.json`, `docs/public-health-ambulance-source-qualification-20260825.json`, `evidence/wp007-real-slice/manifest.json`, `tests/test_public_dataset_archive_plan.py` | Second-family archive receipt is verified; reconciliation, currentness, completeness, authoritative ambulance coverage, isolated role-separated clean-room agent reproduction and release authority remain open |
| `FACILITY-OSM-FOOD-SERVICE-PACKET-20260803` | Content-addressed OpenStreetMap-derived New Zealand food-service assertions are available for bounded reconciliation | `config/archive-sources/osm-new-zealand-food-service-2026.json`, `tests/test_public_dataset_archive_plan.py`, [open_social_data run 30754134781](https://github.com/edithatogo/open_social_data/actions/runs/30754134781) | Source-specific assertions only; no completeness, authority or national facility claim |
| `FACILITY-MARLBOROUGH-FOOD-PREMISE-PACKET-20260803` | Content-addressed Marlborough District Council food-premise licence assertions are available as a second independent public source family | `config/archive-sources/marlborough-food-premise-licences-2026.json`, [open_social_data run 30754246343](https://github.com/edithatogo/open_social_data/actions/runs/30754246343) | Regional source only; no national completeness or authoritative facility claim |
| `FACILITY-HAMILTON-FOOD-PREMISE-PACKET-20260803` | Content-addressed Hamilton City Council food-premise assertions provide a third independent public source family | `config/archive-sources/hamilton-food-premise-register-2026.json`, [open_social_data run 30754473415](https://github.com/edithatogo/open_social_data/actions/runs/30754473415) | Regional source only; no national completeness or authoritative facility claim |
| `FACILITY-SOURCE-FAMILY-GATE-20260803` | Three independent public source families are archived and the source-family gate is satisfied | `docs/facility-source-family-qualification-20260803.json`, `tests/test_public_dataset_archive_plan.py` | Pairwise reconciliation, stratified metrics and panel disposition remain open |
| `FACILITY-SOURCE-MATERIALIZATION-20260803` | Payload digests and record counts were verified directly from the three immutable hosted packets | `scripts/materialize_archived_food_sources.py`, `docs/facility-source-materialization-20260803.json`, `tests/test_public_dataset_archive_plan.py` | Hamilton packet has null geometry for all 3,245 records; geometry/reconciliation qualification remains open |
| `FACILITY-FOOD-RECONCILIATION-20260803` | Deterministic matching ran on the two spatially usable packets while preserving source-only disagreement | `scripts/qualify_archived_food_reconciliation.py`, `docs/facility-food-reconciliation-20260803.json`, `tests/test_public_dataset_archive_plan.py` | 39 candidate matches are not adjudicated; Hamilton is attribute-only and panel qualification remains open |
| `FACILITY-PANEL-QUALIFICATION-20260803` | Methods, provenance and governance dispositions qualify candidate generation without authoritative promotion | `docs/facility-panel-qualification-20260803.json`, `tests/test_public_dataset_archive_plan.py` | Reviewed matches remain zero; stratified adjudication or candidate-only release decision remains open |
| `FACILITY-PANEL-FRAME-QUALIFICATION-20260825` | Four-lens agent panel qualifies the deterministic bounded review frame without asserting factual facility adjudication | `docs/facility-panel-frame-qualification-20260825.json`, `tests/test_facility_panel_frame_qualification.py` | Frame is reproducible; factual pair/sample review, isolated role-separated clean-room agent reproduction, publication and accountable authority gates remain open |
| `FACILITY-PANEL-MANIFEST-CONTRACT-20260829` | Fail-closed shape contract for a future content-bound facility panel rerun | `scripts/validate_facility_panel_manifest.py`, `docs/facility-panel-manifest-contract-20260829.json`, `tests/test_facility_panel_manifest.py` | Contract validation is complete; the existing frame packet lacks role/session/model bindings, so G.1 remains partial |
| `FACILITY-ACCESSIBILITY-BINDING-20260825` | Versioned public-only registry projection bound to an accessibility reference matrix | `src/riopa_provenance/accessibility.py::bind_public_facility_registry`, `docs/facility-accessibility-binding-20260825.json`, `tests/test_accessibility.py`, `tests/test_facility_registry.py` | Stale/private destinations fail closed; binding remains reference-only and does not establish real network, timetable, national-scale or operational validity |
| `FACILITY-ACCESSIBILITY-BINDING-PANEL-20260825` | Four-lens agent-panel qualification of the repository-owned binding contract | `docs/facility-accessibility-binding-panel-review-20260825.json` | Contract qualified for bounded scope; real-source, external participation, publication and authority gates remain open |
| `FACILITY-STRATIFIED-REVIEW-SAMPLE-20260803` | Deterministic bounded strata define the candidate, OSM-only and Marlborough-only review frame | `scripts/build_facility_review_sample.py`, `docs/facility-stratified-review-sample-20260803.json`, `tests/test_public_dataset_archive_plan.py` | Frame is reproducible; panel disposition and any authority decision remain open |
| `FACILITY-HISTORY-EVENTS-20260822` | Append-only opening, closure, relocation, rebrand and source-disagreement history | `src/riopa_provenance/facility_registry.py`, `tests/test_facility_registry.py`, `docs/facility-history-contract.md` | Date/evidence validation and deterministic non-authoritative snapshot pass; source adjudication remains open |
| `FACILITY-PUBLIC-RELEASE-FILTER-20260822` | Sensitive/restricted release filtering | `src/riopa_provenance/facility_registry.py`, `tests/test_facility_registry.py`, `docs/facility-history-contract.md` | Public-only projection excludes restricted, sensitive and controlled assertions while retaining an exclusion ledger; raw packets remain unchanged |
| `FACILITY-DISAGREEMENT-COVERAGE-20260822` | Deterministic bounded disagreement and coverage report over archived assertions | `src/riopa_provenance/facility_registry.py`, `tests/test_facility_registry.py` | Report is non-authoritative and scoped to supplied archived assertions; panel adjudication, completeness and release gates remain open |
| `FACILITY-ACCESSIBILITY-BRIDGE-20260824` | Public-only, non-authoritative facility assertion projection into accessibility opportunity weights | `src/riopa_provenance/accessibility.py:public_facility_opportunities`, `tests/test_accessibility.py` | Restricted rows are excluded and unit weights are explicit; planning integration, capacity and authoritative registry claims remain open |
| `FACILITY-SNAPSHOT-CORRECTION-20260824` | Content-addressed public-only snapshot and append-successor correction contract | `src/riopa_provenance/facility_registry.py:build_snapshot_record`, `src/riopa_provenance/facility_registry.py:validate_snapshot_record`, `tests/test_facility_registry.py` | Payload integrity and predecessor preservation are validated; publication and accountable release approval remain open |
| `FACILITY-SNAPSHOT-VERSION-20260825` | Explicit registry version and predecessor digest validation for public-only snapshot candidates | `src/riopa_provenance/facility_registry.py`, `docs/facility-snapshot-version-contract-20260825.json`, `tests/test_facility_registry.py` | Version and correction shape are machine-checked; publication, factual completeness and accountable release approval remain open |
| `FACILITY-HAMILTON-DISPOSITION-20260825` | Explicit attribute-only disposition for the Hamilton packet with null geometry preserved | `docs/facility-panel-qualification-20260803.json`, `docs/facility-food-reconciliation-20260803.json`, `tests/test_public_dataset_archive_plan.py` | All 3,245 rows remain attribute-only; geometry, completeness, authority and publication gates remain open |

| `FACILITY-PUBLIC-PLANNING-ADAPTER-20260825` | Public-only facility assertion snapshots can provide bounded planning candidates while preserving source identity | `src/riopa_provenance/facility_location.py:candidates_from_public_facility_snapshot`, `docs/facility-public-planning-adapter-contract-20260825.json`, `tests/test_facility_location.py` | Adapter is non-authoritative and promotion-disabled; planning authority, canonical identity and operational availability remain open |

## Repository-owned closeout slice (2026-08-25)

The bounded public-source facility assertions, deterministic reconciliation,
history, release filtering, accessibility bridge, disagreement report and
correction contract are linked above and pass `bash scripts/ci_quality.sh` at
protected `main` revision `7f6f08ac63b010db5c690688d74bc225dee737ad`. This is a
non-authoritative regional technical-preview projection. It does not establish
national completeness, authoritative facility identity, ambulance coverage,
planning integration or operational use.

## Blocking defects

- Independent reproduction issue #149 has no role-separated agent-operator journey record.
- National authoritative ambulance coverage, supermarket-source rights, agent-panel-qualified
  performance estimates and beta/RC/stable release authority remain open gates.
- Hosted merge-policy gate resolved by owner-authorized administrative merge of PR #177
  (`458b53dd6a023cbe15edf7bbb3e24613a13ebbdb`) after all required checks passed; the
  exception bypasses normal protection and is not release evidence. The superseded
  PR #175 blocker is retained only in historical review records, not as a current gate.

## Decisions, exceptions and limitations

- The bounded comparison reports one 5.660 m candidate pair and three source-only assertions.
  It is not a national completeness, currency or accuracy estimate.
- Advisory review is performed by an orchestrated panel of agent analysts; the sole developer remains accountable, and no second-human sign-off is claimed or required for repository-owned review.
- This is a single-developer repository. Agent-panel assessment cannot
  substitute for factual owner-authorized agent-operated user/operator journey evidence or accountable
  release-authority approval.
- Missing geometry, rights, panel disposition, preservation and elapsed-time
  evidence is pending, not negative evidence.

## Review and handover

Required agent-panel lenses: Governance analyst, Provenance analyst, Data-governance analyst, Scientific-methods analyst.

This index is deliberately non-assertive while the track remains `active`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, agent-panel qualified where required, and sufficient for the applicable release gates.
