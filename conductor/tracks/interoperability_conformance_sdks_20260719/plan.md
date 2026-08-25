# Plan: interoperability_conformance_sdks_20260719

## 1. Normative conformance corpus

- [x] 1.1 Define language-neutral positive, negative and migration fixtures. Evidence: `conformance/v1/corpus.json` (four existing canonical/schema cases plus a digest-bound migration case), validated by `tests/test_conformance.py` and `tests/test_interoperability_conformance_contract.py`.
- [x] 1.2 Define expected validation, hashing and lineage-query results. Evidence: `conformance/v1/corpus.json`, `scripts/verify_conformance_parity.py`, and `docs/conformance-and-release-verification.md`; lineage-query results remain explicitly outside this bounded corpus.
- [x] 1.3 Publish extension and profile-version negotiation rules. Evidence: `schemas/interoperability-conformance-contract.schema.json`, `docs/interoperability-conformance-contract-20260822.json`, and `docs/interoperability-conformance-contract-20260822.md`.

## 2. Independent implementations

- [x] 2.1 Stabilise the Python reference SDK and validator. Evidence: `src/riopa_provenance/sdk.py`, `tests/test_sdk.py`, and `docs/python-reference-sdk-20260825.md`; deterministic schema/crosswalk reports pass, while independent and release gates remain open.
- [~] 2.2 Implement a bounded dependency-free Rust typed model and validation. Evidence: `rust/riopa-conformance/`, `docs/rust-conformance-model-contract-20260825.json`, and the hosted `Run bounded Rust conformance model` check; JSON corpus parity, independent producer/consumer interoperability and signed release conformance remain open.
- [x] 2.3 Implement a transport-neutral lineage/query client contract. Evidence: `src/riopa_provenance/lineage.py` and `tests/test_lineage.py`; strict versioned request round-trips are local-only and carry no endpoint or credential semantics.

## 3. Standards and compatibility testing

- [x] 3.1 Add bounded PROV-O-shaped, OpenLineage-shaped, RO-Crate and DSSE/in-toto round-trip tests. Evidence: `docs/interoperability-standards-roundtrip-contract-20260825.json`, `tests/test_standards_roundtrip_contract.py`; external producer/consumer interoperability, full validator qualification and trusted signing remain open.
- [x] 3.2 Generate a bounded cross-version and cross-tool compatibility matrix. Evidence: `scripts/build_interoperability_matrix.py` and `docs/ontology/interoperability-compatibility-matrix-20260825.json`; Rust, standards round-trips and external producer/consumer exercises remain open.
- [~] 3.3 Run bounded producer/consumer interoperability exercises. A dependency-free Rust/Python wire-format exchange is tested in both directions; external independent implementations, standards-complete serialization and signed release reports remain open (`rust/riopa-conformance/src/bin/conformance_exchange.rs`, `tests/test_rust_producer_consumer.py`, `docs/interop-producer-consumer-exercise-20260825.json`).

## 4. Stable SDK and conformance release

- [~] 4.1 Resolve semantic-loss and migration findings. A fail-closed ledger now resolves only the recorded migration-corpus item and keeps Rust parity, external producer/consumer and standards-round-trip findings open (`scripts/build_interoperability_findings.py`, `tests/test_interoperability_findings.py`, `docs/interoperability-findings-ledger-contract-20260825.json`).
- [~] 4.2 Freeze supported v1 SDK surfaces and support ownership. The bounded
  Python and Rust surfaces, compatibility rules and single-maintainer support
  model are documented; external implementation and release gates remain open
  (`docs/interoperability-v1-sdk-support-and-reporting-20260825.md`,
  `docs/interoperability-v1-sdk-support-contract-20260825.json`,
  `tests/test_interoperability_v1_support.py`).
- [~] 4.3 Publish conformance-report implementation guidance. The required
  digest, command, result, semantic-loss, signer and authority fields are
  specified, but the report remains unsigned until trusted signing and factual
  external evidence exist.

## Track closeout

- [x] C.1 Link implementation, test, review, migration and release evidence in `index.md` for the repository-owned closeout slice; external implementation, signing, preservation and authority gates remain explicitly pending (`docs/interoperability-closeout-evidence-20260825.json`, `tests/test_interoperability_closeout_evidence.py`; `22945ef`).
- [ ] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [ ] C.4 Update metadata status and target-release evidence through the Conductor workflow.
