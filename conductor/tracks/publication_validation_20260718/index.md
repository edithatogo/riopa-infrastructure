# Evidence index: Independent validation, release and publication programme

- **Track ID:** `publication_validation_20260718`
- **Status:** `specified`
- **Target release:** `0.9.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Reference`
- **Risk / priority:** `High` / `P1`
- **V1 critical:** `yes`
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Publication and validation lead
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/129

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| `WP-003-resumable-publication-20260731` | GitHub, Hugging Face and Zenodo publication steps are resumable, idempotent and conflict-safe | `src/riopa_provenance/publication.py`, `tests/test_publication.py`, `docs/publication-state.md` | Pure state and receipt reconciliation tests pass; no remote publication performed |
| `WP-006-prepublication-attestation-check-20260731` | GitHub release creation is gated on successful verification of every registered artifact attestation | `.github/workflows/release.yml`, `docs/conformance-and-release-verification.md` | Workflow configured and policy-valid; no release, external reproduction or independent validation is claimed |
| `WP-010-reviewer-ready-synthetic-benchmark-20260801` | A fixed benchmark and independent standard-library verifier provide a bounded clean-room exercise | `examples/wp010-synthetic-benchmark/`, `scripts/build_wp010_reviewer_bundle.py`, `tests/test_wp010_benchmark.py` | Repository-owned reproduction passes; named external reviewer execution and signed evidence remain pending |
| `WP-010-independent-review-protocol-20260801` | Clean-room environment, independence, result and content-binding requirements are explicit | `docs/independent-reproduction-protocol.md`, `docs/preservation-deposit-plan.md` | Protocol ready for external execution; no reviewer, deposit, DOI or release approval is claimed |

## Blocking defects

- None recorded.

## Decisions, exceptions and limitations

- None recorded.

## Review and handover

Required reviewer roles: Governance reviewer, Research-object reviewer, External user reviewer, Scientific reviewer.

This index is deliberately non-assertive while the track remains `specified`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, independently reviewed where required, and sufficient for the applicable release gates.
