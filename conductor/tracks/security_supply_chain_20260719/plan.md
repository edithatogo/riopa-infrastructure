# Plan: security_supply_chain_20260719

## 1. Threat and trust model

- [x] 1.1 Model assets, actors, trust boundaries and abuse cases. (docs/security-threat-model.md)
- [x] 1.2 Classify credentials, environments, sources and release authorities. (docs/security-threat-model.md)
- [x] 1.3 Define severity, response and release-blocking rules. (docs/vulnerability-response-policy.md)

## 2. CI and dependency hardening

- [ ] 2.1 Add branch protection, required automated checks, agent-panel qualification evidence and least-privilege workflow permissions.
- [ ] 2.2 Add dependency, static, secret, container and action-integrity checks.
- [x] 2.3 Generate and validate SBOMs for packages and containers. (existing workflow and security-control-manifest.json)

## 3. Signing and provenance

- [ ] 3.1 Emit DSSE/in-toto-compatible attestations for builds and releases.
- [ ] 3.2 Sign release manifests, tags and distributed artifacts using documented policy.
- [ ] 3.3 Provide offline and CI verification commands and negative tests.

## 4. Audit and incident exercise

- [ ] 4.1 Conduct orchestrated security agent-panel qualification and resolve findings.
- [ ] 4.2 Exercise credential compromise, malicious input and rollback scenarios.
- [x] 4.3 Publish the supported-version and vulnerability-response policy. (docs/vulnerability-response-policy.md)

## 5. Review fixes

- [x] 5.1 Add a machine-readable repository security-control manifest and immutable-action regression tests. (security-control-manifest.json; tests/test_security_controls.py)
- [x] 5.2 Correct the control manifest and remove duplicate plan numbering. (review fix)

## Track closeout

- [ ] C.1 Link implementation, test, review, migration and release evidence in `index.md`.
- [ ] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [ ] C.4 Update metadata status and target-release evidence through the Conductor workflow.
