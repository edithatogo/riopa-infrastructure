# Plan: interoperability_conformance_sdks_20260719

## 1. Normative conformance corpus

- [x] 1.1 Define language-neutral positive, negative and migration fixtures.
- [x] 1.2 Define expected validation, hashing and lineage-query results.
- [x] 1.3 Publish extension and profile-version negotiation rules.

## 2. Independent implementations

- [x] 2.1 Stabilise the Python reference SDK and validator.
- [x] 2.2 Implement Rust models and conformance validation.
- [x] 2.3 Implement a transport-neutral lineage/query client contract.

## 3. Standards and compatibility testing

- [x] 3.1 Add PROV-O, OpenLineage, RO-Crate and attestation round-trip tests.
- [x] 3.2 Generate the cross-version and cross-tool compatibility matrix.
- [x] 3.3 Run independent producer/consumer interoperability exercises.

## 4. Stable SDK and conformance release

- [x] 4.1 Resolve semantic-loss and migration findings.
- [x] 4.2 Freeze supported v1 SDK surfaces and support ownership.
- [x] 4.3 Publish signed conformance reports and implementation guidance.

## Track closeout

- [x] C.1 Link implementation, test, review, migration and release evidence in `index.md`.
- [x] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [x] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [x] C.4 Update metadata status and target-release evidence through the Conductor workflow.
