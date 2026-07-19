# Track: Security, integrity and software supply-chain hardening

Track ID: `security_supply_chain_20260719`  
Phase: **Foundation**  
Target release: **0.3.0**  
Maturity target: **M6**  
Stability class: **Governance**  
V1 critical: **yes**

## Goal

Make source capture, CI, release and distribution trustworthy through threat modelling, least privilege, signed artifacts, dependency integrity and exercised incident response.

## v1 role

This track is part of the stable v1 release contract. It is complete only when its implementation, compatibility, quality, security/governance, operational and reproducibility evidence satisfy both this specification and every applicable blocking gate in `conductor/releases.json` and `conductor/v1-gate.json`.

## Dependencies


- `foundation_architecture_20260718`

## Scope

- Threat models for connectors, archives, CI/CD, publishing, tokens and third-party services.
- Branch protection, code review, environment separation and least-privilege credentials.
- Dependency pinning, SBOMs, vulnerability scanning and reproducible build inputs.
- Signed commits/tags where feasible, DSSE/in-toto attestations and release verification.
- Security reporting, incident response, key compromise, rollback and recovery exercises.

## Out of scope

- Guaranteeing that upstream public services are secure or continuously available.
- Storing real secrets, credentials or restricted payloads in fixtures.

## Requirements

- **R01.** No production credential is available to untrusted pull-request code.
- **R02.** Every released binary, container and research object is linked to reviewed source and CI identity.
- **R03.** Actions, dependencies and containers are pinned by immutable identity for release workflows.
- **R04.** Security findings have severity, owner, due date and release-blocking policy.
- **R05.** Integrity controls distinguish accidental corruption from authenticated authorship.

## Acceptance criteria

- [ ] A threat model covers source spoofing, dependency compromise, credential theft, malicious data, publication tampering and denial of service.
- [ ] CI enforces dependency review, static analysis, secret scanning, action pinning and protected release environments.
- [ ] Releases include verifiable SBOMs, signed checksums and provenance attestations.
- [ ] No unmitigated critical or high vulnerability remains at v1; approved exceptions are time limited and public where safe.
- [ ] A credential compromise and release rollback exercise passes.
- [ ] Security and vulnerability disclosure policies name response targets and supported versions.

## Hardening and maturity gates

- M2 requires executable proof, negative tests and traceable evidence; interfaces may remain experimental.
- M3 requires real-data integration, migration evidence and representative failure handling.
- M4 requires repeated operation, external use, SLO evidence and bounded compatibility changes.
- M5 requires frozen interfaces, independent review, security/performance/recovery qualification and release-candidate soak.
- M6 requires supported compatibility, signed and preserved releases, external reproduction, named maintainers and post-release verification.
- Exceptions must be machine-readable, scoped, approved, time-limited and visible in release evidence.

## Evidence required

- Threat model and security architecture review.
- CI and release-policy configuration.
- SBOM, signature and attestation verification reports.
- Vulnerability register and incident/rollback exercise evidence.

## Risks

- Security controls create an unusable contributor workflow.
- Signed artifacts are produced but never independently verified.
- Malicious or malformed source data exploit parsers or resource limits.
- A release depends on unpinned mutable third-party actions or images.

## Completion rule

The track may enter `complete` only after every acceptance criterion is evidenced in `index.md`, all blocking dependencies are complete, required migrations and documentation are published, and the target release readiness evaluator reports no track-specific blocker.
