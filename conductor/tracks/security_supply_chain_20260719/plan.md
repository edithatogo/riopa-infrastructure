# Plan: security_supply_chain_20260719

## 1. Threat and trust model

- [x] 1.1 Model assets, actors, trust boundaries and abuse cases. (docs/security-threat-model.md)
- [x] 1.2 Classify credentials, environments, sources and release authorities. (docs/security-threat-model.md)
- [x] 1.3 Define severity, response and release-blocking rules. (docs/vulnerability-response-policy.md)

## 2. CI and dependency hardening

- [~] 2.1 Add branch protection, required automated checks, agent-panel qualification evidence and least-privilege workflow permissions. Repository workflow permissions are executable-tested; hosted branch protection and panel evidence remain external gates.
- [~] 2.2 Add dependency, static, secret, container and action-integrity checks. Repository dependency, static, secret and action-integrity checks pass; hosted secret-scanning, container and Renovate/Codecov activation remain external gates.
- [x] 2.3 Generate and validate SBOMs for packages and containers. (existing workflow and security-control-manifest.json)

## 3. Signing and provenance

- [~] 3.1 Emit DSSE/in-toto-compatible attestation envelopes for builds and releases. Evidence: `src/riopa_provenance/attestation.py`, `docs/security-dsse-intoto-contract-20260824.json`, `tests/test_attestation.py`; trusted signing and protected release execution remain pending.
- [~] 3.2 Define deterministic signing manifests and verification policy for release manifests, tags and distributed artifacts. Evidence: `src/riopa_provenance/release_signing.py`, `docs/security-release-signing-contract-20260824.json`, `tests/test_release_signing.py`; trusted signing and protected-tag execution remain pending. (contract commit: `4a722fc0673c1a17d5cbf02843482dc6323fbc34`)
- [x] 3.3 Provide offline and CI verification commands and negative tests. Evidence: `docs/conformance-and-release-verification.md`, `.github/workflows/release.yml`, `docs/security-offline-verification-contract-20260822.json`, and `tests/test_security_offline_verification_contract.py`; execution remains protected-tag gated.

## 4. Audit and incident exercise

- [~] 4.1 Define a digest-bound orchestrated security agent-panel rerun packet and validator. Evidence: `src/riopa_provenance/security_panel.py`, `docs/security-panel-rerun-contract-20260824.json`, `tests/test_security_panel.py`; factual panel execution and qualification remain pending. (contract commit: `a9ffae55774fec5efe4971b5421bfaf6c00bfd9a`)
- [~] 4.2 Define and validate credential-compromise, malicious-input and rollback exercise packets. Evidence: `src/riopa_provenance/security_exercises.py`, `docs/security-incident-exercise-contract-20260824.json`, `tests/test_security_exercises.py`; actual execution receipts remain pending. (contract commit: `0bd5c74b8a7e0301ad69ebaa87364d1626314856`)
- [x] 4.3 Publish the supported-version and vulnerability-response policy. (docs/vulnerability-response-policy.md)

## 5. Review fixes

- [x] R.7 Replace the Bandit-triggering boolean credential field with an explicit `credential_material: absent` value. Evidence: `src/riopa_provenance/security_exercises.py`, full quality harness. (review-fix commit: `cb64b48`)
- [x] R.6 Correct strict MyPy narrowing in the release-signing manifest validator. Evidence: `src/riopa_provenance/release_signing.py`, focused and full quality validation. (review-fix commit: `c63a39c`)
- [x] 5.1 Add a machine-readable repository security-control manifest and immutable-action regression tests. (security-control-manifest.json; tests/test_security_controls.py)
- [x] 5.2 Correct the control manifest and remove duplicate plan numbering. (review fix)
- [x] 5.3 Restore evidence-backed task states after review found that commit `7a61d9b` promoted the track without its required dependency or M2-M6 evidence. (`f6e0a1c`; review fix)

## Track closeout

- [ ] C.1 Link implementation, test, review, migration and release evidence in `index.md`.
- [ ] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [ ] C.4 Update metadata status and target-release evidence through the Conductor workflow.
