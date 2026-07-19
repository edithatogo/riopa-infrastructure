# Plan: interoperability_conformance_sdks_20260719

## 1. Normative conformance corpus

- [ ] 1.1 Define language-neutral positive, negative and migration fixtures.
- [ ] 1.2 Define expected validation, hashing and lineage-query results.
- [ ] 1.3 Publish extension and profile-version negotiation rules.

## 2. Independent implementations

- [ ] 2.1 Stabilise the Python reference SDK and validator.
- [ ] 2.2 Implement Rust models and conformance validation.
- [ ] 2.3 Implement a transport-neutral lineage/query client contract.

## 3. Standards and compatibility testing

- [ ] 3.1 Add PROV-O, OpenLineage, RO-Crate and attestation round-trip tests.
- [ ] 3.2 Generate the cross-version and cross-tool compatibility matrix.
- [ ] 3.3 Run independent producer/consumer interoperability exercises.

## 4. Stable SDK and conformance release

- [ ] 4.1 Resolve semantic-loss and migration findings.
- [ ] 4.2 Freeze supported v1 SDK surfaces and support ownership.
- [ ] 4.3 Publish signed conformance reports and implementation guidance.

## Track closeout

- [ ] C.1 Link implementation, test, review, migration and release evidence in `index.md`.
- [ ] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [ ] C.4 Update metadata status and target-release evidence through the Conductor workflow.
