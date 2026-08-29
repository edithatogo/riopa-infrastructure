# Plan: publication_validation_20260718

## 1. Validation protocol

- [x] 1.1 Define agent-panel conformance, clean-room and agent-user workflow protocols. Evidence: `docs/single-developer-agent-panel-review-policy.md`, `docs/independent-reproduction-protocol.md`, `docs/release-gate-evidence-matrix.md`, `tests/test_hosted_evidence.py`.
- [x] 1.2 Define claim-to-evidence and exploratory/confirmatory classifications. (`docs/publication-claim-classification-contract-20260825.json`, `tests/test_publication_claim_classification.py`; publication, participant and authority gates remain open.)
- [x] 1.3 Select agent-panel validators, environments and analyst-independence criteria. (`docs/publication-validator-selection-contract-20260825.json`, `tests/test_publication_validator_selection.py`; factual participant and authority gates remain open.)

## 2. Release and citation packages

- [x] 2.1 Coordinate immutable software, schema, ontology, data, model and research-object versions. (`docs/publication-version-coordination-20260825.json`, `tests/test_publication_version_coordination.py`; candidate coordination only, publication gates remain open)
- [x] 2.2 Prepare DOI-ready metadata, citation, provenance, SBOM, attestation and preservation sequence. The packet links repository contracts and exact build inputs; deterministic multi-target receipt reconciliation is covered by `src/riopa_provenance/publication.py::reconcile_publication_receipts`, `docs/publication-receipt-reconciliation-contract-20260825.json` and `tests/test_publication.py`. Protected attestations, accepted deposit/restore, participant evidence and authority remain open (`docs/publication-validation-packet-20260825.json`, `tests/test_publication_validation_packet.py`).
- [x] 2.3 Verify discovery, install, query, reproduce and cite workflows. (`docs/publication-workflow-verification-20260825.json`, `tests/test_publication_workflow_verification.py`; bounded local synthetic verification only)

## 3. Agent reproduction

- [x] 3.1 Reproduce one real-data archive release with an owner-authorized agent. The WP-007 bounded real-data packet and three materialized artifacts are digest-bound at the protected-main revision in `docs/publication-real-data-release-candidate-20260825.json`; external participation and publication remain open.
- [x] 3.2 Reproduce one applied benchmark with an owner-authorized agent. The manifest-bound WP-010 benchmark and resilience contract pass on protected `origin/main`; the run and environment are recorded by digest in `docs/publication-applied-benchmark-reproduction-20260825.json`. The national result remains a projection and cannot close the national-scale gate.
- [x] 3.3 Resolve findings and publish deviations/limitations. The real-data and applied-benchmark findings are consolidated with explicit limitations and retained open gates in `docs/publication-deviations-limitations-20260825.json`; no promotion is enabled.

## 4. Publications and correction

- [x] 4.1 Prepare infrastructure, methods, data-descriptor and applied publication package matrices. Candidate references and required checks are explicit as an unpublished repository-owned package; protected attestation, preservation acceptance, isolated role-separated clean-room agent reproduction, elapsed qualification and authority remain open (`docs/publication-package-preparation-20260825.json`, `tests/test_publication_package_preparation.py`).
- [x] 4.2 Exercise correction, supersession and downstream-impact notification. Bounded predecessor/successor package validation and digest-reuse rejection pass; production downstream notification remains open. (`validate_correction_package`, tests)
- [x] 4.3 Publish bounded preview citation guidance and validation-evidence references (`docs/publication-citation-guidance-20260825.json`, `tests/test_publication_citation_guidance.py`). Stable publication, preservation, isolated role-separated clean-room agent reproduction, elapsed and authority gates remain open.

## 5. Bounded agent-panel preparation

- [x] 5.5 Validate the DOI-ready preparation packet's referenced contracts, unpublished status and explicit pending external/elapsed gates (`scripts/validate_publication_validation_packet.py`, `docs/publication-validation-packet-integrity-20260829.json`, `tests/test_publication_validation_packet_validator.py`).

- [x] 5.4 Harden citation-readiness validation to require a lowercase exact 40-character hexadecimal revision that resolves to a commit; CI uses full history so historical candidate bindings can be verified (`scripts/validate_publication_citation_readiness.py`, `.github/workflows/validate.yml`, `tests/test_publication_citation_readiness.py`, `docs/publication-citation-revision-validation-20260829.json`).
  Git revision rather than only a 40-character placeholder, with negative
  coverage and an explicit non-publication boundary
  (`scripts/validate_publication_citation_readiness.py`,
  `docs/publication-citation-revision-validation-20260829.json`,
  `tests/test_publication_citation_readiness.py`).

- [x] 5.1 Define the WP-010 clean-room procedure, independence criteria and content-bound evidence record. (37510dd)
- [x] 5.2 Define the staged Software Heritage plus artifact-repository preservation sequence without claiming a deposit. (37510dd)
- [x] 5.3 Execute three isolated agent lenses across all 28 tracks and publish the fail-closed orchestrator synthesis. (`docs/panel-reports/20260802/manifest.json`)

## Track closeout

- [x] C.1 Link implementation, test, review, migration and release evidence in `index.md` for the repository-owned slice; external publication and participant gates remain explicitly pending.
- [x] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [x] C.4 Update metadata status and target-release evidence through the Conductor workflow; status remains `active`/M1 because the documented gates are unresolved.

## Review fixes

- [x] R2 Reject duplicate target IDs within one receipt batch while retaining idempotent replay across separate calls (`src/riopa_provenance/publication.py`, `tests/test_publication.py`, `docs/publication-receipt-batch-cardinality-20260829.json`). Remote acceptance, preservation, external, elapsed and authority gates remain open.

- [x] R1 Review receipt-batch ordering, replay idempotence, plan/operation binding and malformed-entry rejection. (`src/riopa_provenance/publication.py::reconcile_publication_receipts`, `tests/test_publication.py`, `docs/publication-receipt-reconciliation-contract-20260825.json`)
