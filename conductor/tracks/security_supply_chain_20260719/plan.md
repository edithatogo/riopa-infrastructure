# Plan: security_supply_chain_20260719

## 1. Threat and trust model

- [x] 1.1 Model assets, actors, trust boundaries and abuse cases. (docs/security-threat-model.md)
- [x] 1.2 Classify credentials, environments, sources and release authorities. (docs/security-threat-model.md)
- [x] 1.3 Define severity, response and release-blocking rules. (docs/vulnerability-response-policy.md)

## 2. CI and dependency hardening

- [ ] 2.1 Add branch protection, required review and least-privilege workflow permissions.
- [ ] 2.2 Add dependency, static, secret, container and action-integrity checks.
- [ ] 2.3 Generate and validate SBOMs for packages and containers.

## 3. Signing and provenance

- [ ] 3.1 Emit DSSE/in-toto-compatible attestations for builds and releases.
- [ ] 3.2 Sign release manifests, tags and distributed artifacts using documented policy.
- [ ] 3.3 Provide offline and CI verification commands and negative tests.

## 4. Audit and incident exercise

- [ ] 4.1 Conduct security review and resolve findings.
- [ ] 4.2 Exercise credential compromise, malicious input and rollback scenarios.
- [x] 4.3 Publish the supported-version and vulnerability-response policy. (docs/vulnerability-response-policy.md)

## Track closeout

- [ ] C.1 Link implementation, test, review, migration and release evidence in `index.md`.
- [ ] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [ ] C.4 Update metadata status and target-release evidence through the Conductor workflow.
