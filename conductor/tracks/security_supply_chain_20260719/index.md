# Evidence index: Security, integrity and software supply-chain hardening

- **Track ID:** `security_supply_chain_20260719`
- **Status:** `active`
- **Target release:** `0.3.0`
- **Current maturity:** `M1`
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
| `SEC-RENOVATE-CODECOV-CONTEXT-20260803` | Dependency automation, coverage thresholds and solo-maintainer security context are declared without claiming hosted activation | `renovate.json`, `codecov.yml`, `docs/renovate-codecov-rollout-20260803.json`, `docs/security-control-manifest.json` | Repository configuration is complete; Renovate app, Codecov repository and hosted secret-scanning receipts remain external |
| `SECURITY-WORKFLOW-PERMISSIONS-20260822` | Fail-closed top-level and job-level workflow permissions | `tests/test_security_controls.py`, `.github/workflows/*.yml` | Repository policy passes; hosted branch-protection configuration and agent-panel qualification remain external gates |

## Blocking defects

- Foundation dependency completion, hosted release-environment verification,
  SBOM/signature execution, credential-compromise and rollback exercise, and
  security agent-panel qualification remain pending.

## Decisions, exceptions and limitations

- None recorded.

## Review and handover

Required agent-panel lenses: API/schema analyst, Security analyst, Operations analyst, Research-object analyst.

## Review record

- Review scope: current track records, specification acceptance criteria,
  dependency state, hosted evidence and panel reports through `f6e0a1c`.
- High finding: commit `7a61d9b` changed the track from M1/active to M6/complete,
  removed recorded blockers, and marked every task complete without the required
  foundation dependency or M2-M6 evidence.
- Fix: restored evidence-backed task states, M1/active metadata, the complete
  evidence register and explicit blockers. The track remains unarchived.

This index records the repository-owned M1 implementation slice while the track
remains `active`. Status may advance only through `conductor/workflow.md`;
evidence must be immutable or version-addressed, agent-panel qualified where
required, and sufficient for the applicable release gates.
