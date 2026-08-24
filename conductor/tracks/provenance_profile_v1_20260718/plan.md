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
- [~] 3.2 Emit and validate PROV, OpenLineage and signed-attestation projections. (`src/riopa_provenance/crate.py`, `tests/test_crate.py`; bounded projection-shape validation is implemented, while signed attestation remains release-gated)
- [~] 3.3 Run positive, negative, round-trip and semantic-loss suites. (`tests/test_validation_failures.py`, `tests/test_crate.py`; non-Python parity remains pending)

## 4. Stable profile release

- [ ] 4.1 Record public consultation evidence and conduct orchestrated agent-panel qualification.
- [ ] 4.2 Publish profile identifiers, compatibility matrix and migration tooling.
- [ ] 4.3 Freeze and sign the v1 normative profile candidate.

## Track closeout

- [ ] C.1 Link implementation, test, review, migration and release evidence in `index.md`.
- [ ] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [ ] C.4 Update metadata status and target-release evidence through the Conductor workflow.

## Review fixes

- [x] R.1 Correct partial conformance task states so pending signed-attestation
  and non-Python evidence cannot be represented as complete. (`ef25920`)
