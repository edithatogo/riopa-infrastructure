# Evidence index: Security, integrity and software supply-chain hardening

- **Track ID:** `security_supply_chain_20260719`
- **Status:** `complete`
- **Target release:** `0.3.0`
- **Current maturity:** `M6`
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

## Blocking defects

- None recorded.

## Decisions, exceptions and limitations

- None recorded.

## Review and handover

Required reviewer roles: API/schema reviewer, Security reviewer, Operations reviewer, Research-object reviewer.

This index is deliberately non-assertive while the track remains `complete`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, independently reviewed where required, and sufficient for the applicable release gates.
