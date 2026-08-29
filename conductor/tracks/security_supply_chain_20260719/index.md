# Evidence index: Security, integrity and software supply-chain hardening

- **Track ID:** `security_supply_chain_20260719`
- **Status:** `validating`
- **Target release:** `0.3.0`
- **Current maturity:** `M2`
- **Maturity target:** `M6`
- **Stability class:** `Governance`
- **Risk / priority:** `Critical` / `P0`
- **V1 critical:** `yes`
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Programme owner
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/24

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| `WP-002-dns-pinning-20260731` | Source-spoofing and server-side request-forgery controls | `src/riopa_provenance/capture.py`, `tests/test_capture.py` | Public-address validation, connection pinning, Host preservation and TLS SNI preservation tested |
| `WP-006-attestation-verification-20260731` | Protected-tag assets and checksum inventory are registered as GitHub attestation subjects and verified before release creation | `.github/workflows/release.yml`, `docs/conformance-and-release-verification.md` | Immutable action policy passes; execution remains contingent on a protected release tag and environment |
| `SEC-M1-THREAT-20260801` | Threat, credential and vulnerability response baseline | `docs/security-threat-model.md`, `docs/vulnerability-response-policy.md` | Repository policy recorded; hosted controls and exercises remain pending |
| `SEC-M1-CONTROLS-20260801` | Machine-readable security control inventory and immutable-action regression test | `docs/security-control-manifest.json`, `tests/test_security_controls.py` | Repository checks passing; hosted execution remains pending |
| `SEC-HOSTED-TRUST-20260802` | Additional hosted runner and dependency choices remain explicit and least-privilege | `docs/remaining-gates-autonomous-plan-20260802.json`, `.github/workflows/evidence-campaign.yml`, `scripts/record_hosted_evidence.py` | GitHub workflow uses read-only permissions and immutable action pins; no remote mutation or new runtime dependency |
| `SEC-HF-RUNNER-PREFLIGHT-20260802` | Hugging Face runner use is revision/image pinned, cost bounded and secret free before submission | `docs/hugging-face-evidence-runner-plan-20260802.json` | Staged only; no billable job or new trust boundary activated |
| `SEC-HF-RUNNER-ATTEMPT-20260802` | A secondary hosted recovery attempt uses a digest-pinned image, exact revision, no secrets and a bounded timeout | `docs/hugging-face-evidence-runner-plan-v2-20260802.json`, `docs/remaining-gates-campaign-v3-20260802.json`, `scripts/hf_hosted_recovery.py`, `tests/test_hf_hosted_recovery.py` | Submission rejected with HTTP 402 before job creation; no hosted result claimed and GitHub remains the primary runner |
| `SEC-MAIN-PROTECTION-DRIFT-20260802` | Live branch protection is verified through the authoritative review-enablement flag and exact required-check set | `scripts/verify_github_main_protection.py`, `tests/test_github_main_protection.py`, `docs/github-main-protection-20260802.json` | GraphQL confirms reviews disabled, strict checks/admin/linear/conversation enabled and destructive ref operations disabled; misleading legacy subresource behavior documented |
| `SEC-MAIN-PROTECTION-OBSERVATION-20260825` | Fresh live verification of protected `main` and the Python 3.14 required-check set | `scripts/verify_github_main_protection.py`, `tests/test_github_main_protection.py`, `docs/github-main-protection-20260825.json` | Live verifier passes; hosted provider scanning, Renovate/Codecov activation and agent-panel qualification remain external gates |
| `SEC-GITHUB-SCAN-OBSERVATION-20260825` | Live GitHub secret-scanning, Dependabot and code-scanning endpoint observation | `docs/github-security-observation-20260825.json`, `tests/test_security_controls.py` | 0 open secret-scanning alerts, 2 Dependabot alerts and 0 code-scanning alerts observed; remediation, Renovate/Codecov activation and container scanning remain open |
| `SEC-DEPENDABOT-REMEDIATION-20260825` | Fixed Dependabot advisories are bound to patched versions in `uv.lock` | `docs/github-dependabot-remediation-20260825.json`, `tests/test_security_controls.py`, `uv.lock` | `cryptography` 50.0.0 and `pytest` 9.1.1 satisfy the reported first patched versions; hosted automation and broader scanning gates remain open |
| `SEC-RENOVATE-CODECOV-CONTEXT-20260803` | Dependency automation, coverage thresholds and solo-maintainer security context are declared without claiming hosted activation | `renovate.json`, `codecov.yml`, `docs/renovate-codecov-rollout-20260803.json`, `docs/security-control-manifest.json` | Repository configuration is complete; Renovate app, Codecov repository and hosted secret-scanning receipts remain external |
| `SECURITY-WORKFLOW-PERMISSIONS-20260822` | Fail-closed top-level and job-level workflow permissions | `tests/test_security_controls.py`, `.github/workflows/*.yml` | Repository policy passes; hosted branch-protection configuration and agent-panel qualification remain external gates |
| `SECURITY-OFFLINE-VERIFY-20260822` | Checksums and GitHub attestation verification commands are documented with required inputs and non-claims | `docs/security-offline-verification-contract-20260822.json`, `docs/conformance-and-release-verification.md`, `.github/workflows/release.yml`, `tests/test_security_offline_verification_contract.py` | Repository contract passes; protected-tag execution, signed release assets and independent verification remain open |
| `WP-001-MODULE-COVERAGE-20260825` | Python 3.14 full-suite module and branch-aware coverage inventory | `scripts/build_module_coverage_inventory.py`, `docs/module-coverage-inventory-20260825.json`, `tests/test_module_coverage_inventory.py` | 90% gate is measured without weakening; imported-module failure injection and hosted/release gates remain distinct |
| `SECURITY-DSSE-INTOTO-20260824` | Deterministic DSSE/in-toto-compatible envelope builder with fail-closed unsigned boundary | `src/riopa_provenance/attestation.py`, `docs/security-dsse-intoto-contract-20260824.json`, `tests/test_attestation.py` | Repository envelope and negative tests pass; trusted signing, protected release execution and independent verification remain open |
| `SECURITY-RELEASE-SIGNING-20260824` | Deterministic release signing manifest and fail-closed verification policy | `src/riopa_provenance/release_signing.py`, `docs/security-release-signing-contract-20260824.json`, `tests/test_release_signing.py` | Candidate manifest and negative tests pass; trusted signing, protected-tag execution and accountable release approval remain open |
| `SECURITY-RELEASE-SIGNING-HARDENING-20260829` | Signed manifests require exact revision and verified provider/attestation bindings | `src/riopa_provenance/release_signing.py`, `tests/test_release_signing.py`, `docs/security-release-signing-hardening-20260829.json` | Validator hardening passes; no trusted signature or release approval is asserted |
| `SECURITY-RELEASE-SIGNING-BINDING-20260829` | Signed attestation revision and artifact digests must structurally match the candidate manifest | `src/riopa_provenance/release_signing.py`, `tests/test_release_signing.py` | Structural binding and negative drift tests pass; cryptographic provider verification remains external |
| `SECURITY-RELEASE-SIGNING-ROBUSTNESS-20260829` | Malformed signed inputs and builder revisions fail closed without incidental exceptions | `src/riopa_provenance/release_signing.py`, `tests/test_release_signing.py` | Exception paths are covered by negative tests; trusted signing remains external |
| `WP006-DSSE-INPUT-ROBUSTNESS-20260829` | Malformed DSSE/in-toto builder and decoder inputs return controlled errors | `src/riopa_provenance/attestation.py`, `tests/test_attestation.py`, `docs/wp006-dsse-input-robustness-20260829.json` | Negative tests pass; trusted signing and external interoperability remain open |
| `SECURITY-INCIDENT-EXERCISE-20260824` | Secret-free credential-compromise, malicious-input and rollback exercise packet contract | `src/riopa_provenance/security_exercises.py`, `docs/security-incident-exercise-contract-20260824.json`, `tests/test_security_exercises.py` | Planned packet and negative tests pass; factual execution, hosted rollback and agent-panel qualification remain open |
| `SECURITY-INCIDENT-EXECUTION-20260824` | Digest-bound execution-report validator for all required incident controls | `src/riopa_provenance/security_exercises.py:validate_exercise_execution`, `tests/test_security_exercises.py` | Local contract passes; no execution or qualification is claimed |
| `SECURITY-PANEL-RERUN-20260824` | Digest-bound three-lens panel rerun packet validator with preserved dissent boundary | `src/riopa_provenance/security_panel.py`, `docs/security-panel-rerun-contract-20260824.json`, `tests/test_security_panel.py` | Pending packet and complete-packet negative tests pass; factual panel execution and qualification remain open |
| `SECURITY-NEGATIVE-COVERAGE-20260825` | Expanded fail-closed negative coverage for panel and release-signing contracts | `tests/test_security_panel.py`, `tests/test_release_signing.py`, `docs/module-coverage-inventory-20260825.json` | Invalid packet, role, digest, artifact, policy and verification paths are exercised; trusted signing, hosted execution and factual qualification remain open |
| `SECURITY-EXERCISE-NEGATIVE-COVERAGE-20260825` | Expanded fail-closed negative coverage for planned incident and execution-report contracts | `tests/test_security_exercises.py`, `docs/module-coverage-inventory-20260825.json` | Scenario, control, environment, credential-shaped and execution-report failure paths are exercised; factual execution and hosted rollback remain open |
| `SECURITY-BOUNDED-CONTRACT-CLOSEOUT-20260825` | Repository-owned attestation, release-signing, incident-exercise and panel-packet contracts are complete with explicit non-claims | `src/riopa_provenance/attestation.py`, `src/riopa_provenance/release_signing.py`, `src/riopa_provenance/security_exercises.py`, `src/riopa_provenance/security_panel.py`, and focused tests | Deterministic construction and negative validation pass; trusted signing, hosted execution and factual qualification remain open |
| `SECURITY-M2-PROMOTION-20260826` | Exact-tree threat/control, immutable-action, attestation/signing, negative-test, SBOM and exercise-packet evidence | `docs/security-m2-promotion-20260826.json`, `tests/test_security_m2_promotion.py`, [PR #616](https://github.com/edithatogo/riopa-infrastructure/pull/616) | Promoted to experimental M2 only; hosted execution, repeated operation, recovery/panel qualification and stable authority remain open |
| `WP006-STRICT-CYCLONEDX-VALIDATION-20260829` | Generated SBOMs pass the locked official CycloneDX 1.6 JSON schema in local and hosted quality lanes | `scripts/validate_cyclonedx_sbom.py`, `scripts/build_sbom.sh`, `tests/test_cyclonedx_validation.py`, `.github/workflows/validate.yml`, `.github/workflows/security.yml` | Portable strict validation replaces shallow assertions; separate-tool and release-asset verification remain distinct gates |
| `WP006-HOSTED-SBOM-VALIDATION-20260829` | Exact merged revision executes strict SBOM validation in the dedicated hosted security lane | `docs/wp006-hosted-sbom-validation-20260829.json`, [run 33232065327](https://github.com/edithatogo/riopa-infrastructure/actions/runs/33232065327) | Hosted run and digest-bearing retained artifact pass; separate-tool, preservation, signing and protected-release gates remain open |

## Repository-owned closeout slice (2026-08-24)

The implementation, focused tests, review fixes and generated project metadata
for the current repository-owned slice are linked above. The authoritative
validation command is `bash scripts/ci_quality.sh`; it must pass from the
protected `main` revision before this slice is treated as publishable.

The following gates are deliberately not inferred from local contracts:

- hosted branch-protection and release-environment verification;
- protected-tag trusted signing, SBOM publication and independent verification;
- factual credential-compromise, malicious-input and rollback execution;
- factual security agent-panel execution and qualification; and
- accountable release-authority approval for any promotion.

These are external or elapsed evidence gates, not missing implementation. No
release, beta, RC or stable-v1 promotion is authorized by this record.

## Blocking maturity gates

- M3 requires hosted protection/release-environment verification and factual
  SBOM, signature and provenance execution.
- M4 requires repeated security operation and SLO evidence.
- M5 requires credential-compromise/rollback recovery qualification and the
  orchestrated security agent-panel qualification.
- M6 requires accountable stable-release authority approval.

The foundation dependency is M2 and therefore satisfies this experimental M2
boundary. Dependency maturity remains evaluated separately for every later
release threshold.

## Decisions, exceptions and limitations

- The repository is single-developer operated. Review lenses are performed by
  agent panels; they do not substitute for factual hosted execution,
  independent reproduction or accountable-authority approval.
- Public, bounded, non-operational technical-preview scope remains in force.
- Missing hosted or participant evidence is recorded as pending, never as a
  negative result or waiver.

## Review and handover

Required agent-panel lenses: API/schema analyst, Security analyst, Operations analyst, Research-object analyst.

## Review record

- Review scope: current track records, specification acceptance criteria,
  dependency state, hosted evidence and panel reports through
  `482bdf8cfadcb4ec4a9f65d13fc6c1baf1c079e7`.
- High finding: commit `7a61d9b` changed the track from M1/active to M6/complete,
  removed recorded blockers, and marked every task complete without the required
  foundation dependency or M2-M6 evidence.
- Fix: restored evidence-backed task states, M1/active metadata, the complete
  evidence register and explicit blockers. The track remains unarchived.
- 2026-08-24 closeout review: implementation and repository-owned validation
  links were reconciled; C.1, C.2 and C.4 are complete for this slice. C.3
  remains open because the external and elapsed gates above are unresolved.

This index records the repository-owned implementation at experimental M2 while
the track remains `validating`. The executable controls, deterministic
attestation/signing contracts, negative tests, SBOM construction and exercise
packet validators satisfy M2 only. Evidence for M3-M6 must be immutable or
version-addressed, agent-panel qualified where required, and sufficient for the
applicable later release gates.
