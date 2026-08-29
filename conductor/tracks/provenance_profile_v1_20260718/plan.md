# Plan: provenance_profile_v1_20260718

## 1. Native evidence mapping

- [x] 1.1 Map fyi-cli, fyi-archive, nlp-policy-nz, corpus and healthpoint evidence. (`docs/provenance-profile-mapping-inventory-20260801.md`)
- [x] 1.2 Classify exact, approximate, conflicting, extension and unmapped semantics. (`docs/provenance-profile-mapping-inventory-20260801.md`)
- [x] 1.3 Define additive dual-emission and migration boundaries. (`docs/provenance-and-lineage.md`, `docs/provenance-profile-mapping-inventory-20260801.md`)

## 2. Normative contract implementation

- [x] 2.1 Adopt named canonical JSON and cryptographic identity rules. (`src/riopa_provenance/hashing.py`, `schemas/provenance-event.schema.json`)
- [x] 2.2 Define stream, partition, retry, idempotency, checkpoint and causal-parent semantics. (`src/riopa_provenance/validation.py`, `src/riopa_provenance/retry.py`, `tests/test_validation_failures.py`)
- [x] 2.3 Add manual, adjudication and AI-assistance facets. (`docs/provenance-and-lineage.md`, `schemas/provenance-event.schema.json`)

## 3. Cross-language and projection conformance

- [x] 3.1 Implement Python and non-Python validators/models for the bounded
  language-neutral corpus. (`scripts/conformance_node.mjs`,
  `bindings/typescript/provenance-event-v1.d.ts`, `tests/test_conformance.py`)
- [x] 3.2 Emit and validate bounded PROV and OpenLineage projection shapes and the signed-attestation boundary. (`src/riopa_provenance/crate.py`, `tests/test_crate.py`; projection-shape validation passes, while trusted signed attestation remains release-gated.)
- [x] 3.3 Run the bounded positive, negative and round-trip suites with Python/Node parity receipt. (`tests/test_validation_failures.py`, `tests/test_crate.py`, `tests/test_conformance_parity_receipt.py`; semantic-loss qualification and full profile parity remain pending.)

## 4. Stable profile release

- [x] 4.1 Conduct the repository-owned orchestrated agent-panel qualification. Four lenses assess the bounded profile and preserve open non-Python, semantic-loss, publication, signed-attestation and authority gates; this does not substitute for those gates (`docs/provenance-profile-panel-qualification-20260825.json`, `tests/test_provenance_profile_panel_qualification.py`).
- [x] 4.2 Define the bounded profile compatibility matrix and migration fixture. (`docs/provenance-profile-compatibility-matrix-20260825.json`, `docs/provenance-profile-migration-1.0.0-to-1.1.0.json`, `tests/test_conformance.py`; additive migration validation passes, while the persistent publication identifier and stable release remain open.)
- [x] 4.3 Freeze an unsigned, digest-bound v1 normative profile candidate (`docs/provenance-profile-v1-candidate-freeze-20260825.json`, `tests/test_provenance_profile_candidate_freeze.py`). Signing, publication, full semantic/non-Python, isolated role-separated clean-room agent reproduction and authority gates remain open.

## Track closeout

- [x] C.1 Link implementation, test, review, migration and release evidence in `index.md` for the repository-owned projection slice; signed, publication and panel gates remain explicitly pending.
- [x] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [x] C.4 Update metadata status and target-release evidence through the Conductor
  workflow; the initial closeout remained `validating`/M1 before the bounded R.2
  promotion to M2.

## Review fixes

- [x] R.1 Correct partial conformance task states so pending signed-attestation
  and non-Python evidence cannot be represented as complete. (`ef25920`)
- [x] R.2 Revalidate the canonical event, retry, lineage and assistance contracts,
  negative fixtures, Python/Node parity, bounded projections, migration contract
  and digest-bound candidate on the merged tree, then promote only this track to
  experimental M2. (`docs/provenance-m2-promotion-20260827.json`,
  `tests/test_provenance_m2_promotion.py`)
- [x] R.3 Reconcile C.4 and the evidence index with the bounded M2 decision while
  retaining all M3-M6 integration, operation, publication, reproduction and
  authority gates. (Conductor review fix)
