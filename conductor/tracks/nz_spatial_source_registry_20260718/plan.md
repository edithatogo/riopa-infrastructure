# Plan: nz_spatial_source_registry_20260718

## 1. Authority and plan baseline

- [x] 1.1 Create bounded current/historical authority and jurisdiction records. Evidence: `docs/nz-spatial-registry-baseline-20260822.json`; completeness remains open.
- [x] 1.2 Record the bounded pilot plan/source-family status and official/archive references without implying a national inventory. Evidence: `docs/nz-spatial-registry-baseline-20260822.json`, `docs/public-dataset-archive-incorporation-plan-20260802.json`.
- [x] 1.3 Register exact-version LINZ and Stats NZ sources plus explicitly disabled NZTA/network, planning, Gazette and legislation families with archive disposition. Evidence: `docs/nz-spatial-registry-baseline-20260822.json`, `config/source-registry/nz-spatial-pilot.yaml`, `tests/test_nz_spatial_registry_baseline.py`.
- [x] 1.4 Register the exact Stats NZ Meshblock 2026 item, edition, service, rights and immutable hosted archive evidence without implying that the other national source families are complete.

## 2. Service and document discovery

- [x] 2.1 Record the bounded pilot's declared WFS/OGC and Koordinates mechanisms without live discovery or national completeness claims. (`config/source-registry/nz-spatial-pilot.yaml`, `src/riopa_provenance/registry.py:classify_connector_readiness`, `docs/nz-spatial-connector-readiness-contract-20260824.json`; commit `39d028e`)
- [ ] 2.2 Discover plan documents, provision structures and legal-status evidence.
- [ ] 2.3 Preserve capability, metadata, terms and rights snapshots before any source is incorporated into a canonical or analytical projection.

## 3. Versioning and health

- [ ] 3.1 Implement source/service/version identity and change events.
- [ ] 3.2 Add automated health, disappearance and terms-change checks.
- [x] 3.3 Produce connector-readiness and unresolved-source classifications from declared registry fields; live health and authority remain open. (`src/riopa_provenance/registry.py:classify_connector_readiness`, `tests/test_source_registry_readiness.py`, `docs/nz-spatial-connector-readiness-contract-20260824.json`; commit `39d028e`)

## 4. National review and release

- [ ] 4.1 Complete records for every current authority.
- [ ] 4.2 Conduct independent sample audit and correct findings.
- [ ] 4.3 Publish immutable registry and coverage releases.

## Track closeout

- [ ] C.1 Link implementation, test, review, migration and release evidence in `index.md`.
- [ ] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [ ] C.4 Update metadata status and target-release evidence through the Conductor workflow.

## Review fixes

- [x] R1 Fail closed on unknown authentication types and malformed capability arrays in readiness projections. (`src/riopa_provenance/registry.py`, `tests/test_source_registry_readiness.py`; commit `f78743a`)
