# Plan: nz_spatial_archive_mvp_20260718

## 1. Real source capture

- [x] 1.10 Capture standalone Tasman item rights and prepare a closed, licensed layer-only public packet on Actions from unchanged capture bytes (`4bd89c5`; `docs/tasman-hosted-preparation-20260830.json`, run 33301038921); public upload and rebuild acceptance remain separate.
- [x] 1.11 Publish the licensed Tasman packet from verified private preservation through Actions, verify every public byte anonymously at an immutable revision, and rebuild canonical, GeoParquet and DuckDB representations twice without live-source contact (`4093254`; `docs/tasman-publication-acceptance-20260830.json`, run 33303579649, public revision `73be6f6d5b7d1297458ed49e7222a46f915dc5a2`).

- [x] 1.9 Run council captures in bounded parallel GitHub Actions jobs, preserve complete and failed attempts in private Hugging Face storage, publish unrestricted evidence, and verify immutable bytes before accepting source-level checkpoints (`docs/hosted-council-preservation-20260830.json`; run 33298342091 attempts 1/2; QLDC acquisition remains incomplete).

- [x] 1.1 Select Wellington City, Queenstown Lakes, New Plymouth and Tasman after the national source inventory, using four materially different official publication mechanisms while keeping rights, capture, legal-status and representativeness gates open (`docs/nz-spatial-council-selection-20260825.json`, `tests/test_nz_spatial_council_selection.py`; `e37b398`).
- [ ] 1.2 Archive exact-version national layers, council services and planning documents faithfully before incorporating their named snapshots.
- [~] 1.3 Preserve bounded rights, capability, legal-status and source-health evidence for existing archived packets. The archive-only record is fail-closed: unobserved live health, unresolved rights and operative legal status remain explicit (`docs/nz-spatial-archive-rights-capability-health-20260830.json`, `schemas/nz-spatial-archive-rights-capability-health.schema.json`, `tests/test_nz_spatial_archive_rights_capability_health.py`).
- [x] 1.4 Acquire and verify the complete Stats NZ Meshblock 2026 supporting-geography packet at immutable GitHub and Hugging Face revisions.
- [x] 1.5 Project the immutable Meshblock packet into content-addressed RIOPA source and capture records without contacting its live service (`8f34bfd`).
- [x] 1.6 Verify and consume the immutable public WCC Churton Park packet offline, binding every packet path, byte count, digest, capture identity and object reference while retaining CC-BY-3.0-NZ attribution and non-authority boundaries (`docs/wcc-public-archive-spatial-projection-20260830.json`, `tests/test_public_archive_spatial.py`).
- [x] 1.7 Capture all 130 distinct New Plymouth Volume 3 PDF links plus the index (97,420,678 response bytes), verify each retained HTTP/object receipt and reject partial responses. Raw documents remain outside Git; operative status, public-payload rights and capture-to-release qualification remain open (`docs/npdc-map-document-capture-20260830.json`, `scripts/capture_npdc_map_documents.py`, `tests/test_npdc_map_document_capture.py`).

- [x] 1.8 Capture the exact Tasman GeoHUB group inventory (3 + 111 items), terms and all 3,655 catalogue-linked TRMP zones features in 12 HTTP captures / 24,899,154 retained bytes. Raw bytes remain local; catalogue observation is not source currency, operative status or an atomic snapshot (`docs/tasman-geohub-capture-20260830.json`, `scripts/capture_tasman_catalogue.py`, `tests/test_tasman_catalogue_capture.py`).

## 2. Canonical bitemporal model

QLDC acquisition follow-up: the current official entry page and user guide are
captured, but both linked application routes returned HTTP 403 from this
environment. `docs/qldc-eplan-route-qualification-20260830.json` records all four
responses; `scripts/qualify_qldc_eplan.py` reruns a bounded four-request probe.
This does not complete 1.2 or count the guide as a planning-data capture. Next:
qualify a council-published export or ordinary interactive access, without
bypassing access controls; meanwhile continue Tasman canonical materialisation.


- [ ] 2.1 Transform source layers into canonical feature/version records.
- [ ] 2.2 Preserve original geometry and produce separately evidenced repairs.
- [ ] 2.3 Link source, document and plan identities without unsupported interpretation.
- [x] 2.4 Build a normalized Meshblock feature projection with page-level capture lineage and no implicit geometry repair (`8f34bfd`, `61cddd3`; projection `urn:riopa:projection:sha256:64a1cbce366794b2b802f04dbe2bf1dc5fbf813e5c5b159bcf0782af9adc511f`).
- [x] 2.5 Build one canonical WCC feature identity with explicit unknown valid time, archive-recorded time, geometry digest and capture lineage; no operative-plan or current-supermarket status is inferred (`docs/wcc-public-archive-spatial-projection-20260830.json`).
- [x] 2.6 Rebuild all 3,655 archived Tasman zone features into canonical records with capture lineage, original geometry digests and unknown valid/operative time from the anonymously verified public packet (`docs/tasman-publication-acceptance-20260830.json`).

## 3. Materialisation and quality

- [x] 3.11 Integrate receipt-bound cycle ledger persistence into the Tasman Actions workflow with verified immutable Hugging Face checkpoints, concurrent-writer reconciliation and failure receipts; keep scheduled/change/recovery qualification separate (`9c56ef5`; `docs/tasman-cycle-preservation-20260831.md`; `docs/tasman-cycle-preservation-acceptance-20260831.json`, run 33360096774 attempts 1/2 passed).

- [x] 3.10 Implement an offline receipt-bound cycle ledger with predecessor linkage, retry deduplication and corruption/recovery tests; reconcile current preservation summaries without changing historical receipts or qualifying unobserved hosted cycles (`f145368`; `docs/tasman-cycle-ledger-20260831.md`).

- [x] 3.9 Compare Tasman feature identities, attributes and original geometry against the pinned accepted baseline after hosted publication; reject corrupt inputs and distinguish capture metadata changes from data changes without crediting scheduled cycles or recovery qualification (`52cab92`; `docs/tasman-feature-comparison-acceptance-20260831.json`; run 33345370638 passed for all 3,655 features).

- [x] 3.8 Bind preserved Tasman source and derived receipts to verified GitHub source/publication run attempts, distinguish scheduled triggers from manual replay, and retain a deduplication key without claiming change/recovery or release-cycle qualification (`6fdbb81`; `docs/tasman-run-provenance-acceptance-20260831.json`; run 33336884257 attempts 1/2).

- [x] 3.7 Preserve the qualified Tasman canonical, GeoParquet and DuckDB projections publicly through GitHub Actions, verify immutable anonymous bytes and semantics, and replay without replacing the original derived revision. Keep derived payloads outside Git and retain unknown valid time, attribution and release non-claims (`docs/tasman-derived-acceptance-20260831.json`; run 33335595270 attempts 1/2; public revision `1ccd5953893c588f87a31fe77fcd3d6124f03fae`).

- [x] 3.1 Validate the GeoParquet and DuckDB Spatial materialization receipt and query-ready projection links from the content-addressed archived packet, with packet-bound read-only query examples. The 57,575-feature local restoration is path-, size- and digest-bound and passes PyArrow/DuckDB readback; independent target acceptance remains open (`scripts/validate_meshblock_materialization_receipt.py`, `docs/meshblock-materialization-receipt-validation-20260826.json`, `tests/test_meshblock_materialization_receipt_validation.py`, `docs/meshblock-projection-query-examples-20260826.md`, `tests/test_meshblock_projection_query_examples.py`; `1abb123`, `a466a49`).
- [x] 3.2 Run bounded geometry, topology, completeness, temporal, rights-metadata and lineage checks over the immutable Meshblock projection. Population, national authority and broader source checks remain open. (`tests/test_meshblock_projection_evidence.py`, `docs/stats-nz-meshblock-projection-quality-report-20260825.json`; `cdd5a8f`)
- [x] 3.3 Produce bounded coverage, fidelity and unresolved-status reports without promoting supporting geography to population or national evidence. (`docs/stats-nz-meshblock-projection-quality-report-20260825.json`, `tests/test_meshblock_projection_quality_report.py`; `cdd5a8f`)
- [x] 3.4 Validate the complete offline projection and commit bounded evidence while keeping bulk spatial outputs outside Git (`evidence/stats-nz-meshblock-2026-projection/records-manifest.json`).
- [x] 3.5 Rebuild the WCC slice into byte-stable GeoParquet and semantically deterministic DuckDB projections, execute PyArrow/DuckDB readback, and keep the materialized files outside Git (`src/riopa_provenance/public_archive_spatial.py`, `tests/test_public_archive_spatial.py`).
- [x] 3.6 Verify two hosted Tasman rebuilds agree on canonical semantics, GeoParquet bytes and DuckDB semantic readback; keep bulk derived outputs outside Git and distinguish repeatability from isolated clean-room reproduction (`docs/tasman-publication-acceptance-20260830.json`).

## 4. Research-object release

- [ ] 4.1 Generate methods, citation, provenance, SBOM and attestations.
- [ ] 4.2 Run external validation and clean-environment rebuild.
- [ ] 4.3 Publish immutable DOI-ready MVP and correction policy.

## 5. Review fixes

- [x] 5.20 Bind comparison files to source/count/canonical receipt semantics, preserve exact WKB without reserialization, validate canonical lineage and metadata-only differences, and verify corrupted-download recovery after isolated cross-review (`52cab92`; 41 focused tests, strict MyPy/Bandit and full quality/reproducibility pass).
- [x] 5.21 Recompute ledger scheduling classifications from bound run events rather than trusting stored flags after isolated subagent review (`f145368`; 19 ledger tests; no hosted-cycle qualification).

- [x] 5.19 Distinguish a verified Tasman capture from its enclosing failed matrix run, bind archived acquisition/code evidence, pin trigger/publication API attempts, reject invalid calendar/repository/receipt bindings, and resolve the GitHub CLI to an absolute path (`cc61878`; isolated review, 39 focused tests, strict MyPy/Bandit, full quality and reproducibility checks pass; hosted collector acceptance remains separate).

- [x] 5.18 Bind derived-publication rights and full-row readback, preserve canonical time/lineage records, disable external access before DuckDB queries, retain immutable original-manifest checksums and rewrite sanitized failure evidence after durable storage outcomes (`c4f745f`; isolated review, 49 focused tests, full suite 1,545 passed/1 skipped, 90.41% branch-aware coverage against the 90% gate).

- [x] 5.17 Preserve bounded, credential-free failure receipts and durable attempt records when anonymous publication verification or rebuilds fail, without replacing the original public revision or masking the primary error (`85af7d4`; PR #754 hosted review; 34 focused tests and isolated re-review pass).

- [x] 5.13 Reject traversing builder inputs and derive public preparation summaries from verified packet identities/counts; validate receipt hash/name bindings and add negative tests after isolated review.
- [x] 5.14 Validate role-specific ArcGIS query parameters and bind the receipt's rights-object digest to the public candidate after hosted review.
- [x] 5.15 Retain machine-readable hosted coverage even on test failure and refresh the generated module inventory for the new packet builder without weakening the coverage gate (hosted measurement run 33299699887; its below-threshold result remains explicit until successor CI).
- [x] 5.16 Treat ArcGIS geometry fields separately from feature attributes and exercise real-archiver object-ID pagination plus corruption/query failure paths; preserve the 90% whole-package gate.

- [x] 5.12 Correct the GitHub-rejected job-level runner context and test literal work/artifact path binding; serialise overlapping runs per council without cancelling active preservation.

- [x] 5.11 Bind original public revision and evidence sizes/digests in durable hosted checkpoints; verify that exact public revision on replay without replacement, and keep task 1.9 on one parseable issue-generator line after hosted review.

- [x] 5.1 Verify compressed and uncompressed artifact identities, require a retrieval receipt for every projected capture record, safely reuse only a verified local packet, reject redirects outside the archive host boundary and separate stable semantic identity from run-specific DuckDB bytes (`ffeb681`, `6c9c5c8`, `f04693c`, `de8b790`, `61cddd3`).
- [x] 5.2 Bind the WCC packet to a trusted immutable descriptor; enforce exact filesystem, capture and object closure; contain reconstructed object paths; derive the ArcGIS OID from metadata; and limit feature lineage to its page capture after isolated preservation review.
- [x] 5.3 Replace the non-portable DuckDB file digest claim with independently reproduced semantic readback, and generate policy non-claims in the projection receipt after isolated reproduction review.
- [x] 5.4 Prevent outputs from mutating verified inputs, reject unsafe output names and symlinked control files, reconcile the checked-in WCC trust descriptor to the public publication receipt, and bind the captured rights payload to its exact digest, licence text and attribution after preservation re-review.
- [x] 5.5 Fail closed when captured count receipts, the capture-set declaration and materialized rows disagree, while keeping the new page-lineage and metadata-OID behavior opt-in so earlier preserved rebuild identities remain unchanged after hosted review.
- [x] 5.6 Reject partial HTTP 206/Content-Range document and index responses, distinguish retained-byte budgets from transfer volume, and persist structured failure evidence after the NPDC capture subagent review.
- [x] 5.7 Address hosted NPDC review: bounded transient retries charge every retained attempt to the byte budget; index parsing failures persist capture-linked diagnostics; preserve the historical receipt unchanged and explain successor producer fields in `docs/npdc-map-producer-reconciliation-20260830.json`.

- [x] 5.8 Persist incomplete receipts for malformed Tasman layer capabilities and distinguish observed licence links from publication approval after isolated subagent review.
- [x] 5.9 Detect ArcGIS object IDs declared only through `esriFieldTypeOID` field metadata, reject ambiguous declarations and enforce ordered unique-ID capture; preserve the original Tasman manifest and record independent offline uniqueness verification in `docs/tasman-geohub-offline-verification-20260830.json`.
- [x] 5.10 Attribute Hub fetch/configuration failures to the Hub stage rather than the authority page; bind the historical and successor script hashes without changing the original successful capture receipt after hosted review.

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
