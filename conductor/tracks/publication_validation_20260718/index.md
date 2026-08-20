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
| `WP-010-reviewer-ready-synthetic-benchmark-20260801` | A fixed benchmark and standard-library verifier provide a bounded clean-room exercise | `examples/wp010-synthetic-benchmark/`, `scripts/build_wp010_reviewer_bundle.py`, `tests/test_wp010_benchmark.py` | Repository-owned reproduction and the content-bound all-track agent panel pass as bounded evidence; additional agent reproduction remains pending |
| `WP-010-agent-reproduction-protocol-20260801` | Clean-room environment, result and content-binding requirements are explicit for owner-authorized agent execution | `docs/independent-reproduction-protocol.md`, `docs/preservation-deposit-plan.md` | Agent protocol ready; no second-person review, deposit, DOI or release approval is claimed |
| `PUB-AGENT-PANEL-HF-20260802` | Review responsibility and optional public evidence mirror are bounded for a single-developer repository | `docs/single-developer-agent-panel-review-policy.md`, `docs/remaining-gates-autonomous-plan-20260802.json` | Agent-panel review policy active; Hugging Face is optional and not preservation, participant or authority evidence |
| `PUB-HOSTED-CLEAN-ROOM-20260802` | Dependency-isolated verifier runs on an exact revision in a hosted runner | `docs/hosted-evidence-batch-20260802.json`, [GitHub Actions run 30744486356](https://github.com/edithatogo/riopa-infrastructure/actions/runs/30744486356) | Passed for owner-authorized agent rehearsal; elapsed and release-authority evidence remain pending |
| `PUB-SINGLE-DEVELOPER-PANEL-V2-20260802` | Machine-readable gates, templates and live issue sources use agent-panel qualification semantics | `docs/single-developer-agent-panel-review-policy.md`, `docs/remaining-gates-campaign-v2-20260802.md`, `docs/panel-qualification-report-templates-20260801.json` | Review is agent-panel-owned; owner-authorized agent workflow evidence and authority decision remain distinct |
| `PUB-ALL-TRACK-PANEL-20260802` | Three isolated agent lenses and an orchestrator synthesis assess every Conductor track against one frozen revision and archive digest | `docs/panel-reports/20260802/manifest.json`, `scripts/validate_all_track_panel.py`, `tests/test_all_track_panel.py` | Reports complete for all 28 tracks; every final M6 disposition remains not-qualified; one stale facility-registry index finding was repaired after the frozen assessment |
| `PUB-CORRECTION-PACKAGE-20260803` | Immutable predecessor/successor correction package and downstream-notification fields are explicit | `docs/publication-correction-package-20260803.json`, `src/riopa_provenance/governance.py`, `src/riopa_provenance/publication.py`, `tests/test_governance.py`, `tests/test_publication.py` | Bounded WP-010 successor example is recorded; production downstream notification, external reproduction and release-authority acceptance remain open |

## Blocking defects

- None recorded.

## Decisions, exceptions and limitations

- None recorded.

## Review and handover

Required agent-panel lenses: Governance analyst, Research-object analyst, Agent workflow analyst, Scientific-methods analyst.

This index is deliberately non-assertive while the track remains `specified`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, agent-panel qualified where required, and sufficient for the applicable release gates.
