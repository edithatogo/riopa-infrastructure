# Plan: nz_spatial_archive_mvp_20260718

## 1. Real source capture

- [x] 1.1 Select Wellington City, Queenstown Lakes, New Plymouth and Tasman after the national source inventory, using four materially different official publication mechanisms while keeping rights, capture, legal-status and representativeness gates open (`docs/nz-spatial-council-selection-20260825.json`, `tests/test_nz_spatial_council_selection.py`; `e37b398`).
- [ ] 1.2 Archive exact-version national layers, council services and planning documents faithfully before incorporating their named snapshots.
- [ ] 1.3 Preserve rights, capability, legal-status and source-health evidence.
- [x] 1.4 Acquire and verify the complete Stats NZ Meshblock 2026 supporting-geography packet at immutable GitHub and Hugging Face revisions.
- [x] 1.5 Project the immutable Meshblock packet into content-addressed RIOPA source and capture records without contacting its live service (`8f34bfd`).
- [x] 1.6 Verify and consume the immutable public WCC Churton Park packet offline, binding every packet path, byte count, digest, capture identity and object reference while retaining CC-BY-3.0-NZ attribution and non-authority boundaries (`docs/wcc-public-archive-spatial-projection-20260830.json`, `tests/test_public_archive_spatial.py`).
- [x] 1.7 Capture all 130 distinct New Plymouth Volume 3 PDF links plus the index (97,420,678 response bytes), verify each retained HTTP/object receipt and reject partial responses. Raw documents remain outside Git; operative status, public-payload rights and capture-to-release qualification remain open (`docs/npdc-map-document-capture-20260830.json`, `scripts/capture_npdc_map_documents.py`, `tests/test_npdc_map_document_capture.py`).

## 2. Canonical bitemporal model

- [ ] 2.1 Transform source layers into canonical feature/version records.
- [ ] 2.2 Preserve original geometry and produce separately evidenced repairs.
- [ ] 2.3 Link source, document and plan identities without unsupported interpretation.
- [x] 2.4 Build a normalized Meshblock feature projection with page-level capture lineage and no implicit geometry repair (`8f34bfd`, `61cddd3`; projection `urn:riopa:projection:sha256:64a1cbce366794b2b802f04dbe2bf1dc5fbf813e5c5b159bcf0782af9adc511f`).
- [x] 2.5 Build one canonical WCC feature identity with explicit unknown valid time, archive-recorded time, geometry digest and capture lineage; no operative-plan or current-supermarket status is inferred (`docs/wcc-public-archive-spatial-projection-20260830.json`).

## 3. Materialisation and quality

- [x] 3.1 Validate the GeoParquet and DuckDB Spatial materialization receipt and query-ready projection links from the content-addressed archived packet, with packet-bound read-only query examples. The 57,575-feature local restoration is path-, size- and digest-bound and passes PyArrow/DuckDB readback; independent target acceptance remains open (`scripts/validate_meshblock_materialization_receipt.py`, `docs/meshblock-materialization-receipt-validation-20260826.json`, `tests/test_meshblock_materialization_receipt_validation.py`, `docs/meshblock-projection-query-examples-20260826.md`, `tests/test_meshblock_projection_query_examples.py`; `1abb123`, `a466a49`).
- [x] 3.2 Run bounded geometry, topology, completeness, temporal, rights-metadata and lineage checks over the immutable Meshblock projection. Population, national authority and broader source checks remain open. (`tests/test_meshblock_projection_evidence.py`, `docs/stats-nz-meshblock-projection-quality-report-20260825.json`; `cdd5a8f`)
- [x] 3.3 Produce bounded coverage, fidelity and unresolved-status reports without promoting supporting geography to population or national evidence. (`docs/stats-nz-meshblock-projection-quality-report-20260825.json`, `tests/test_meshblock_projection_quality_report.py`; `cdd5a8f`)
- [x] 3.4 Validate the complete offline projection and commit bounded evidence while keeping bulk spatial outputs outside Git (`evidence/stats-nz-meshblock-2026-projection/records-manifest.json`).
- [x] 3.5 Rebuild the WCC slice into byte-stable GeoParquet and semantically deterministic DuckDB projections, execute PyArrow/DuckDB readback, and keep the materialized files outside Git (`src/riopa_provenance/public_archive_spatial.py`, `tests/test_public_archive_spatial.py`).

## 4. Research-object release

- [ ] 4.1 Generate methods, citation, provenance, SBOM and attestations.
- [ ] 4.2 Run external validation and clean-environment rebuild.
- [ ] 4.3 Publish immutable DOI-ready MVP and correction policy.

## 5. Review fixes

- [x] 5.1 Verify compressed and uncompressed artifact identities, require a retrieval receipt for every projected capture record, safely reuse only a verified local packet, reject redirects outside the archive host boundary and separate stable semantic identity from run-specific DuckDB bytes (`ffeb681`, `6c9c5c8`, `f04693c`, `de8b790`, `61cddd3`).
- [x] 5.2 Bind the WCC packet to a trusted immutable descriptor; enforce exact filesystem, capture and object closure; contain reconstructed object paths; derive the ArcGIS OID from metadata; and limit feature lineage to its page capture after isolated preservation review.
- [x] 5.3 Replace the non-portable DuckDB file digest claim with independently reproduced semantic readback, and generate policy non-claims in the projection receipt after isolated reproduction review.
- [x] 5.4 Prevent outputs from mutating verified inputs, reject unsafe output names and symlinked control files, reconcile the checked-in WCC trust descriptor to the public publication receipt, and bind the captured rights payload to its exact digest, licence text and attribution after preservation re-review.
- [x] 5.5 Fail closed when captured count receipts, the capture-set declaration and materialized rows disagree, while keeping the new page-lineage and metadata-OID behavior opt-in so earlier preserved rebuild identities remain unchanged after hosted review.
- [x] 5.6 Reject partial HTTP 206/Content-Range document and index responses, distinguish retained-byte budgets from transfer volume, and persist structured failure evidence after the NPDC capture subagent review.

## Track closeout

- [x] C.1 Link implementation, test, panel, migration and release-candidate evidence in `index.md` for the bounded archive slice; full source coverage, restoration, preservation, external validation and release-authority gates remain explicitly open (`docs/nz-archive-mvp-closeout-evidence-20260829.json`, `tests/test_nz_archive_mvp_closeout_evidence.py`).
- [x] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected. The locked methods generation, roadmap status, issue graph and full quality harness passed; the methods output was temporary and not a release artifact (`docs/nz-archive-mvp-conductor-regeneration-20260825.json`).
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [x] C.4 Update metadata status and target-release evidence through the Conductor workflow; the track remains `active`/M1 with exact dependency, coverage, external-validation, reproduction, release-cycle, preservation/publication and authority blockers.

## Review fixes

- [x] R1 Wrap the quality-report test path so the repository quality gate passes (`edc1fb7`).
- [x] R2 Bind restored materializations to safe receipt paths, sizes and digests; execute packet-bound PyArrow and DuckDB identity/count/null-geometry checks; and correct the documented query columns (`1abb123`).
- [x] R3 Verify the receipt/manifest/projection digest chain and add hermetic CI coverage for successful artifact queries, tamper rejection and unsafe receipt paths (`a466a49`).
- [x] R4 Restore the canonical all-release roadmap status after detecting a mistakenly narrowed regeneration (`f3cf453`).
- [x] R5 Complete the whole-change repository review after two remediation loops with no remaining High/Critical repository-owned finding; full tests, quality and reproducibility pass (`docs/nz-spatial-archive-review-remediation-20260825.json`; `e53b9b0`).
