# Plan: interoperability_conformance_sdks_20260719

## 1. Normative conformance corpus

- [x] 1.1 Define language-neutral positive, negative and migration fixtures. Evidence: `conformance/v1/corpus.json` (four existing canonical/schema cases plus a digest-bound migration case), validated by `tests/test_conformance.py` and `tests/test_interoperability_conformance_contract.py`.
- [x] 1.2 Define expected validation, hashing and lineage-query results. Evidence: `conformance/v1/corpus.json`, `scripts/verify_conformance_parity.py`, and `docs/conformance-and-release-verification.md`; lineage-query results remain explicitly outside this bounded corpus.
- [x] 1.3 Publish extension and profile-version negotiation rules. Evidence: `schemas/interoperability-conformance-contract.schema.json`, `docs/interoperability-conformance-contract-20260822.json`, and `docs/interoperability-conformance-contract-20260822.md`.

## 2. Independent implementations

- [x] 2.1 Stabilise the Python reference SDK and validator. Evidence: `src/riopa_provenance/sdk.py`, `tests/test_sdk.py`, and `docs/python-reference-sdk-20260825.md`; deterministic schema/crosswalk reports pass, while independent and release gates remain open.
- [x] 2.2 Implement a bounded Rust typed model and validation. The Rust runner parses the checked-in corpus and matches all five canonical SHA-256 fixtures (`rust/riopa-conformance/src/bin/conformance_corpus.rs`, `docs/rust-corpus-parity-20260825.json`, `tests/test_rust_producer_consumer.py`). Schema-validity parity, full RFC 8785 number handling and signed release conformance remain open.
- [x] 2.3 Implement a transport-neutral lineage/query client contract. Evidence: `src/riopa_provenance/lineage.py` and `tests/test_lineage.py`; strict versioned request round-trips are local-only and carry no endpoint or credential semantics.

## 3. Standards and compatibility testing

- [x] 3.1 Add bounded PROV-O-shaped, OpenLineage-shaped, RO-Crate and DSSE/in-toto round-trip tests. Evidence: `docs/interoperability-standards-roundtrip-contract-20260825.json`, `tests/test_standards_roundtrip_contract.py`; external producer/consumer interoperability, full validator qualification and trusted signing remain open.
- [x] 3.2 Generate a bounded cross-version and cross-tool compatibility matrix. Evidence: `scripts/build_interoperability_matrix.py` and successor `docs/ontology/interoperability-compatibility-matrix-20260829.json`; seven Python/Node/Rust cases are observed, while external standards round-trips and producer/consumer acceptance remain open.
- [x] 3.3 Run bounded producer/consumer interoperability exercises. The dependency-free Rust/Python wire-format exchange passes in both directions, and a separately implemented Rust client completes capture, validation and lineage-query workflows against a language-neutral fixture. This satisfies the separately implemented branch without claiming external authorship or use; standards-complete serialization and signed release reports remain open (`rust/riopa-conformance/src/bin/{conformance_exchange.rs,client_workflow.rs}`, `conformance/v1/client-workflow.json`, `tests/test_rust_producer_consumer.py`, `docs/separate-rust-client-workflow-20260829.json`).
- [x] 3.4 Validate the published research object with an independently maintained RO-Crate validator, preserve the v0.3.0 failure, and remediate prospective generator output to pass all 65 RO-Crate 1.2 required checks (`docs/wp006-external-rocrate-validation-20260829.json`, `src/riopa_provenance/crate.py`, `tests/test_crate.py`).

## 4. Stable SDK and conformance release

- [x] 4.1 Resolve semantic-loss and migration findings. A fail-closed ledger resolves the recorded migration-corpus item and the bounded Rust/Python canonical-hash parity finding; external producer/consumer, standards-round-trip and signed-report findings remain open (`scripts/build_interoperability_findings.py`, `tests/test_interoperability_findings.py`, `docs/interoperability-findings-ledger-contract-20260825.json`, `docs/rust-corpus-parity-20260825.json`).
- [x] 4.2 Freeze supported v1 SDK surfaces and support ownership. The bounded
  Python and Rust surfaces, compatibility rules and single-maintainer support
  model are documented; external implementation and release gates remain open
  (`docs/interoperability-v1-sdk-support-and-reporting-20260825.md`,
  `docs/interoperability-v1-sdk-support-contract-20260825.json`,
  `tests/test_interoperability_v1_support.py`).
- [x] 4.3 Publish conformance-report implementation guidance. The required
  digest, command, result, semantic-loss, signer and authority fields are
  specified, but the report remains unsigned until trusted signing and factual
  external evidence exist.

## Track closeout

- [x] C.1 Link implementation, test, review, migration and release evidence in `index.md` for the repository-owned closeout slice; the `v0.4.0` preview is now mirrored and DOI-preserved, while broader standards conformance, trusted stable-candidate signing, stable-candidate preservation and authority gates remain pending (`docs/interoperability-closeout-evidence-20260825.json`, `docs/v0.4.0-preservation-wp006-reconciliation-20260829.json`, `tests/test_interoperability_closeout_evidence.py`; `22945ef`).
- [x] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected. The locked methods generation, roadmap status, issue graph and full quality harness passed; the methods output was temporary and not a release artifact (`docs/interoperability-conductor-regeneration-20260825.json`).
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [x] C.4 Update metadata status and target-release evidence through the Conductor workflow; metadata is `validating`/M2 for target release `0.6.0`. `v0.4.0` preview preservation is complete; broader claimed-profile conformance, trusted stable-candidate signing and preservation, and authority gates remain unresolved.

## Review fixes

- [x] R1 Review the Rust corpus runner for deterministic ordering, corpus binding, unsupported-number fail-closed behavior and non-promotion language. (`rust/riopa-conformance/src/{lib.rs,bin/conformance_corpus.rs}`, `tests/test_rust_producer_consumer.py`, `docs/rust-corpus-parity-20260825.json`)
- [x] R2 Add a separately implemented Rust client workflow with content-bound capture, required-field validation, bounded reverse-lineage traversal and fail-closed drift tests (`docs/separate-rust-client-workflow-20260829.json`).
- [x] R3 Reject unknown lineage-query fields in the Rust client so its fail-closed field-set semantics match the normative Python contract (`rust/riopa-conformance/src/bin/client_workflow.rs`, `tests/test_rust_producer_consumer.py`; review fix).
- [x] R4 Promote only the bounded interoperability track to experimental M2/validating and stage an OIDC-attested `v0.4.0` software technical preview without passing the separate programme data milestone (`scripts/build_release_conformance_report.py`, `.github/workflows/release.yml`, `tests/test_v040_release_preparation.py`).
- [x] R5 Publish `v0.4.0` from the exact reviewed merge, verify all checksums and GitHub OIDC attestations after download, and preserve the credential-gated Zenodo/Hugging Face contingency without claiming a deposit (`docs/v0.4.0-release-publication-20260829.json`; PRs #661 and #662; release run 33236124879).
- [x] R6 Mirror the six exact release assets and bounded metadata to the public `edithatogo/riopa-evidence-campaign` dataset, bind commit `ebecf6d38084aa459b27ef2bf753505003b08a16`, and anonymously re-download all seven files with byte equality and checksum verification (`docs/v0.4.0-release-mirror-20260829.json`).
- [x] R7 Publish the same six release assets to Zenodo, bind DOI `10.5281/zenodo.22156988`, and anonymously re-download all files with byte equality and SHA-256 manifest verification in another immutable successor receipt (`docs/v0.4.0-zenodo-preservation-20260829.json`).
- [x] R8 Recalculate WP-006 after the Hugging Face and Zenodo successor receipts: preserve the completed `v0.4.0` slice and retain broader standards-complete conformance plus a trusted signed exact-stable-candidate report as the remaining acceptance boundary (`docs/v0.4.0-preservation-wp006-reconciliation-20260829.json`, `tests/test_v040_preservation_wp006_reconciliation.py`).
- [x] R9 Add a machine-checked inventory covering every claimed publication profile, with validator, version, command and explicit bounded/external status; this documents coverage without claiming external certification (`scripts/validate_profile_validator_inventory.py`, `docs/wp006-profile-validator-inventory-20260829.json`, `tests/test_profile_validator_inventory.py`).
- [x] R10 Close the inventory overclaim path by requiring bounded status values and non-empty open-gate/non-claim fields, with negative coverage tests (review fix; 2026-08-29).
- [x] R11 Validate the normative corpus envelope before invoking the Python/Node parity runners, rejecting malformed metadata, unsafe references, duplicate IDs and invalid digests before a parity receipt is emitted (2026-08-29; `scripts/verify_conformance_parity.py`).
- [x] R11 Replace the bounded Rust hash-only runner with maintained RFC 8785 canonicalisation and Draft 2020-12 schema validation, expand the shared corpus with numeric and UTF-16 ordering vectors, and publish an observed Python/Node/Rust successor matrix (`e1e4d68`, `docs/ontology/interoperability-compatibility-matrix-20260829.json`).
- [x] R12 Fail closed on premature stable campaign evidence: technical-preview drills no longer qualify, qualifying observations require an activated campaign and hosted run identity, daily observations must be unique and non-future, and the normative 90-day beta plus 30-day RC thresholds are consistent (`e1e4d68`, `tests/test_campaign_ledger.py`).

- [x] R13 Validate the machine-readable technical-preview report's local
  content-addressed bindings in the release workflow, including repository-
  relative paths, exact SHA-256 digests and explicit copied-evidence
  limitations. This hardens report integrity without claiming signatures,
  publication acceptance or authority (`scripts/validate_release_conformance_report.py`,
  `docs/release-conformance-report-validation-20260829.json`,
  `tests/test_release_conformance_report.py`, `.github/workflows/release.yml`).
- [x] R14 Reconcile stale compatibility-matrix references with the observed 2026-08-29 successor while preserving the 2026-08-25 predecessor snapshot (`docs/wp006-matrix-traceability-20260829.json`, `docs/conformance-and-release-verification.md`).
- [x] R15 Bind the matrix traceability receipt to the exact 40-character merged revision and guard it with a regression test (review fix; 2026-08-29).
- [x] R16 Require positive, negative and migration case classes in the normative corpus before parity execution, with negative coverage for unknown and missing classes (2026-08-29).
- [x] R17 Harden OpenLineage projection validation for non-empty run/job/dataset identity and producer/schema fields, with negative contract coverage (2026-08-29; `docs/wp006-openlineage-projection-validation-20260829.json`).
- [x] R19 Enforce lowercase 64-character SHA-256 subject digests before building unsigned DSSE/in-toto envelopes, with negative contract coverage (2026-08-29; `docs/wp006-dsse-subject-digest-validation-20260829.json`).
- [x] R20 Reject empty PROV graph identifiers in the bounded projection validator, with negative contract coverage (2026-08-29; `docs/wp006-prov-identity-validation-20260829.json`).
- [x] R18 Guard corpus case-class membership by type before set lookup so malformed non-string values fail with structured validation errors (review fix; 2026-08-29).
- [x] R20 Bind the technical-preview report's declared fixture digest to the checked-in client-workflow bytes and reject tampered fixture digests (2026-08-29; `docs/wp006-release-report-fixture-binding-20260829.json`).
- [x] R21 Return a controlled validation result when the release-report CLI receives a JSON scalar or array (review fix; 2026-08-29).
- [x] R22 Add a deterministic local validator for the v0.4.0 successor
  preservation receipts, checking provider coverage, receipt status,
  repository-relative paths and exact digests while retaining the preview/stable
  boundary (`scripts/validate_v040_preservation_receipts.py`,
  `docs/v040-preservation-receipt-validation-20260829.json`,
  `tests/test_v040_preservation_receipt_validator.py`).
