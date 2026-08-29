# Plan: security_supply_chain_20260719

## 1. Threat and trust model

- [x] 1.1 Model assets, actors, trust boundaries and abuse cases. (docs/security-threat-model.md)
- [x] 1.2 Classify credentials, environments, sources and release authorities. (docs/security-threat-model.md)
- [x] 1.3 Define severity, response and release-blocking rules. (docs/vulnerability-response-policy.md)

## 2. CI and dependency hardening

- [x] 2.1 Add branch-protection policy, required automated checks, agent-panel qualification evidence and least-privilege workflow permissions. Repository workflow permissions and policy contracts are executable-tested; hosted branch protection and factual panel execution remain external gates.
- [x] 2.2 Add dependency, static, secret, container and action-integrity checks. Repository dependency, static, secret and action-integrity checks pass; hosted secret-scanning, container and Renovate/Codecov activation remain external gates.
- [x] 2.3 Generate and validate SBOMs for packages and containers. (existing workflow and security-control-manifest.json)

## 3. Signing and provenance

- [x] 3.1 Emit DSSE/in-toto-compatible attestation envelopes for builds and releases. Evidence: `src/riopa_provenance/attestation.py`, `docs/security-dsse-intoto-contract-20260824.json`, `tests/test_attestation.py`; deterministic envelope construction and negative tests pass, while trusted signing and protected release execution remain pending.
- [x] 3.2 Define deterministic signing manifests and verification policy for release manifests, tags and distributed artifacts. Evidence: `src/riopa_provenance/release_signing.py`, `docs/security-release-signing-contract-20260824.json`, `tests/test_release_signing.py`; manifest construction and negative tests pass, while trusted signing and protected-tag execution remain pending. (contract commit: `4a722fc0673c1a17d5cbf02843482dc6323fbc34`)
- [x] 3.3 Provide offline and CI verification commands and negative tests. Evidence: `docs/conformance-and-release-verification.md`, `.github/workflows/release.yml`, `docs/security-offline-verification-contract-20260822.json`, and `tests/test_security_offline_verification_contract.py`; execution remains protected-tag gated.

## 4. Audit and incident exercise

- [x] 4.1 Define a digest-bound orchestrated security agent-panel rerun packet and validator. Evidence: `src/riopa_provenance/security_panel.py`, `docs/security-panel-rerun-contract-20260824.json`, `tests/test_security_panel.py`; packet construction and negative validation pass, while factual panel execution and qualification remain pending. (contract commit: `a9ffae55774fec5efe4971b5421bfaf6c00bfd9a`)
- [x] 4.2 Define and validate credential-compromise, malicious-input and rollback exercise packets. Evidence: `src/riopa_provenance/security_exercises.py`, `docs/security-incident-exercise-contract-20260824.json`, `tests/test_security_exercises.py`; secret-free packet and execution-report validation pass, while actual execution receipts remain pending. (contract commit: `0bd5c74b8a7e0301ad69ebaa87364d1626314856`)
- [x] 4.3 Publish the supported-version and vulnerability-response policy. (docs/vulnerability-response-policy.md)

## 5. Review fixes

- [x] R.7 Replace the Bandit-triggering boolean credential field with an explicit `credential_material: absent` value. Evidence: `src/riopa_provenance/security_exercises.py`, full quality harness. (review-fix commit: `cb64b48`)
- [x] R.6 Correct strict MyPy narrowing in the release-signing manifest validator. Evidence: `src/riopa_provenance/release_signing.py`, focused and full quality validation. (review-fix commit: `c63a39c`)
- [x] 5.1 Add a machine-readable repository security-control manifest and immutable-action regression tests. (security-control-manifest.json; tests/test_security_controls.py)
- [x] 5.2 Correct the control manifest and remove duplicate plan numbering. (review fix)
- [x] 5.3 Restore evidence-backed task states after review found that commit `7a61d9b` promoted the track without its required dependency or M2-M6 evidence. (`f6e0a1c`; review fix)

## Track closeout

- [x] C.1 Link implementation, test, review, migration and release evidence in `index.md` for the repository-owned slice; external execution receipts remain explicitly pending.
- [x] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains; M3 hosted execution, M4 repeated operation, M5 recovery/panel qualification and M6 release-authority gates remain open while the foundation dependency now satisfies M2.
- [x] C.4 Update metadata status and target-release evidence through the Conductor workflow; the initial closeout remained `active`/M1 before the bounded R.8 transition to `validating`/M2.

## M2 promotion

- [x] R.8 Revalidate the threat/control contracts, immutable-action and workflow policies, deterministic attestation/signing manifests, negative tests, SBOM construction and secret-free exercise packets on the merged tree, then promote only this track to experimental M2. (`docs/security-m2-promotion-20260826.json`, `tests/test_security_m2_promotion.py`)
- [x] R.9 Replace the SBOM builder's shallow field assertions with locked official CycloneDX 1.6 strict-schema validation and fail-closed negative tests; the existing quality and security workflows execute the validator in hosted CI (`scripts/validate_cyclonedx_sbom.py`, `scripts/build_sbom.sh`, `tests/test_cyclonedx_validation.py`).
- [x] R.10 Require exact Git revisions and verified provider/attestation bindings for any signed manifest, with a negative test preventing unsigned metadata from masquerading as signed evidence (review fix; 2026-08-29; `docs/security-release-signing-hardening-20260829.json`).
- [x] R.11 Bind declared signed attestation revision and artifact digests structurally to the candidate manifest, and reject malformed builder revisions (review fix; 2026-08-29).
- [x] R.12 Ensure malformed signed artifact arrays and non-string builder revisions fail with controlled validation errors (review fix; 2026-08-29).
- [x] R.13 Guard DSSE/in-toto builders and decoders against malformed non-string/object inputs with controlled errors and negative tests (`docs/wp006-dsse-input-robustness-20260829.json`; 2026-08-29).
- [x] R.14 Guard the DSSE builder and release-report CLI against non-object JSON inputs (review fix; 2026-08-29).
