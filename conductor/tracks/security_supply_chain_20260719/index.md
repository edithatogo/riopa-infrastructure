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
| `SEC-HOSTED-TRUST-20260802` | Additional hosted runner and dependency choices remain explicit and least-privilege | `docs/remaining-gates-autonomous-plan-20260802.json`, `.github/workflows/evidence-campaign.yml`, `scripts/record_hosted_evidence.py` | GitHub workflow uses read-only permissions and immutable action pins; no remote mutation or new runtime dependency; cost approval required before Hugging Face job submission |

## Blocking defects

- Hosted release-environment verification, SBOM/signature execution, credential-compromise and rollback exercise, and independent security review remain pending.

## Decisions, exceptions and limitations

- None recorded.

## Review and handover

Required agent-panel lenses: API/schema analyst, Security analyst, Operations analyst, Research-object analyst.

## Review record

- Review scope: security baseline, control manifest, workflow pinning test and
  Conductor records through `e5ede96`.
- Finding: plan item 2.3 was duplicated, and the manifest overstated secret
  scanning coverage not present in the checked-in workflows.
- Fix: retained one completed 2.3 item and narrowed SC-03 to controls evidenced
  by the repository.

This index records the repository-owned M1 implementation slice while the track remains `active`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, independently reviewed where required, and sufficient for the applicable release gates.
