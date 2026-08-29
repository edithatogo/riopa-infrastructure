# Plan: nz_spatial_source_registry_20260718

## 1. Authority and plan baseline

- [x] 1.1 Create bounded current/historical authority and jurisdiction records. Evidence: `docs/nz-spatial-registry-baseline-20260822.json`; completeness remains open.
- [x] 1.2 Record the bounded pilot plan/source-family status and official/archive references without implying a national inventory. Evidence: `docs/nz-spatial-registry-baseline-20260822.json`, `docs/public-dataset-archive-incorporation-plan-20260802.json`.
- [x] 1.3 Register exact-version LINZ and Stats NZ sources plus explicitly disabled NZTA/network, planning, Gazette and legislation families with archive disposition. Evidence: `docs/nz-spatial-registry-baseline-20260822.json`, `config/source-registry/nz-spatial-pilot.yaml`, `tests/test_nz_spatial_registry_baseline.py`.
- [x] 1.4 Register the exact Stats NZ Meshblock 2026 item, edition, service, rights and immutable hosted archive evidence without implying that the other national source families are complete.

## 2. Service and document discovery

- [x] 2.1 Record the bounded pilot's declared WFS/OGC and Koordinates mechanisms without live discovery or national completeness claims. (`config/source-registry/nz-spatial-pilot.yaml`, `src/riopa_provenance/registry.py:classify_connector_readiness`, `docs/nz-spatial-connector-readiness-contract-20260824.json`; commit `39d028e`)
- [x] 2.2 Build a non-contacting declared-plan discovery queue from supplied registry metadata. The deterministic queue records declared candidates without contacting endpoints; document bytes, provision structures, legal status and authority remain not observed and open (`src/riopa_provenance/registry.py::build_declared_plan_discovery`, `docs/nz-declared-plan-discovery-contract-20260825.json`, `tests/test_registry.py`).
- [x] 2.3 Preserve a content-addressed declared capability, metadata, terms and rights snapshot before source incorporation. The non-contacting snapshot builder is promotion-disabled; payload capture, preservation acceptance and current-authority coverage remain open (`src/riopa_provenance/registry.py:build_declared_source_snapshot`, `docs/nz-source-metadata-snapshot-contract-20260825.json`, `tests/test_source_registry_readiness.py`).

## 3. Versioning and health

- [x] 3.1 Implement source/service/version identity and digest-only change events without endpoint contact. (`src/riopa_provenance/registry.py`, `tests/test_source_registry_readiness.py`; `97857fd`)
- [x] 3.2 Add automated health, disappearance and terms-change checks. Archived declared observations produce fail-closed quarantine actions for degraded, missing, terms-changed and not-observed statuses; live health and authority remain open (`src/riopa_provenance/registry.py:evaluate_declared_source_health`, `docs/nz-source-health-quarantine-contract-20260825.json`).
- [x] 3.3 Produce connector-readiness and unresolved-source classifications from declared registry fields; live health and authority remain open. (`src/riopa_provenance/registry.py:classify_connector_readiness`, `tests/test_source_registry_readiness.py`, `docs/nz-spatial-connector-readiness-contract-20260824.json`; commit `39d028e`)

## 4. National review and release

- [ ] 4.1 Complete records for every current authority.
- [ ] 4.2 Conduct independent sample audit and correct findings.
- [x] 4.3 Build an immutable, unpublished registry and coverage release candidate. The deterministic candidate and coverage projection are content-addressed and promotion-disabled; publication, preservation, current-authority completeness and accountable release authority remain open (`src/riopa_provenance/registry.py::build_registry_release_candidate`, `docs/nz-source-registry-release-candidate-contract-20260825.json`, `tests/test_registry.py`).

## Track closeout

- [x] C.1 Link implementation, test, agent-panel, migration and release-candidate evidence in `index.md` for the repository-owned bounded slice; authority, preservation and external-release gates remain open (`docs/nz-source-registry-closeout-evidence-20260826.json`, `tests/test_nz_source_registry_closeout_evidence.py`).
- [x] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected. The locked methods generation, roadmap status, issue graph and full quality harness passed; the methods output was temporary and not a release artifact (`docs/source-registry-conductor-regeneration-20260825.json`).
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [x] C.4 Promote the bounded registry executable-proof boundary to experimental M2. The track remains `validating`; current-authority completeness, live rights/health evidence, repeated hosted monitoring, preservation, panel reproduction and accountable-owner gates remain assigned to M3-M6 (`docs/nz-source-registry-m2-promotion-20260829.json`, `tests/test_nz_source_registry_m2_promotion.py`).
- [x] C.5 Group missing and existing licence decisions into permissive public-archive tiers, separating copyright permission from authority, completeness and safety (`docs/source-rights-publication-decision-matrix-20260829.json`, `tests/test_source_rights_publication_decision_matrix.py`).
- [x] C.6 Adopt full lawful capture and private preservation as the default unless explicitly restricted, while retaining an affirmative-basis requirement only for public payload copying (`docs/source-rights-archive-default-20260829.json`, `tests/test_source_rights_archive_default.py`).
- [x] C.7 Capture and publicly preserve the three newly qualified Tier-A ArcGIS layers with exact payload, licence and fixity receipts. The merged public revision contains one WCC feature, 224 prototype ambulance points and five Greater Wellington points (`docs/public-tier-a-archive-publication-20260829.json`, `tests/test_public_tier_a_archive_publication.py`).

## M2 review fixes

- [x] R3 Apply the sole-developer subagent-panel policy while preserving factual source-rights, hosted-observation, preservation and owner-authority boundaries.
- [x] R4 Replace blanket permission holds with exact-item and publisher-wide open-licence decisions for the WCC Churton layer, NZ ambulance prototype and Greater Wellington GIS, while retaining provenance, authority and safety limitations (`docs/source-rights-publication-decision-matrix-20260829.json`, `tests/test_source_rights_publication_decision_matrix.py`).
- [x] R5 Confirm the maximal archive default distinguishes explicit retention restrictions from copyright's affirmative public-copying requirement and does not rely on takedown as permission (`docs/source-rights-archive-default-20260829.json`).
- [x] R6 Preserve registry endpoint static query strings when no additional capture parameters are supplied; this prevents ArcGIS licence receipts such as `?f=json` from silently degrading to generic HTML (`src/riopa_provenance/capture.py`, `tests/test_capture.py`).

## Review fixes

- [x] R1 Fail closed on unknown authentication types and malformed capability arrays in readiness projections. (`src/riopa_provenance/registry.py`, `tests/test_source_registry_readiness.py`; commit `f78743a`)
- [x] R2 Review the registry release candidate for deterministic ordering, duplicate-source rejection, digest binding and publication fail-closed semantics. (`src/riopa_provenance/registry.py::build_registry_release_candidate`, `tests/test_registry.py`, `docs/nz-source-registry-release-candidate-contract-20260825.json`)
