# Evidence index: Operations, service reliability and digital preservation

- **Track ID:** `operations_preservation_sre_20260719`
- **Status:** `specified`
- **Target release:** `0.8.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Operational`
- **Risk / priority:** `Critical` / `P0`
- **V1 critical:** `yes`
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Programme owner
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/114

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| `WP-002-capture-observability-20260731` | Capture attempts, outcomes, archived bytes and structured failure categories | `src/riopa_provenance/capture.py`, `tests/test_capture.py` | Deterministic in-process metrics and structured failure events tested |
| `WP-003-publication-resume-20260731` | Publication retry, idempotency and partial-completion semantics | `src/riopa_provenance/publication.py`, `tests/test_publication.py`, `docs/publication-state.md` | Content-bound operation keys, idempotent replay and conflict rejection tested |
| `OPS-REMAINING-GATES-20260802` | Recovery, operational-cycle and RC-soak evidence sequence, executable hosted lanes and reset contingencies | `docs/remaining-gates-autonomous-plan-20260802.json`, `.github/workflows/evidence-campaign.yml`, `scripts/record_hosted_evidence.py`, `schemas/hosted-evidence.schema.json`, `tests/test_hosted_evidence.py` | Revision-bound technical-preview runner implemented; hosted execution and elapsed clocks remain pending actual observations |

## Blocking defects

- None recorded.

## Decisions, exceptions and limitations

- None recorded.

## Review and handover

Required agent-panel lenses: Security analyst, Operations analyst, Research-object analyst, External-user workflow analyst.

This index is deliberately non-assertive while the track remains `specified`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, independently reviewed where required, and sufficient for the applicable release gates.
