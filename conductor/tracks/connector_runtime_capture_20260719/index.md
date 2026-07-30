# Evidence index: Common connector runtime and faithful capture framework

- **Track ID:** `connector_runtime_capture_20260719`
- **Status:** `specified`
- **Target release:** `0.4.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Platform`
- **Risk / priority:** `Critical` / `P0`
- **V1 critical:** `yes`
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Core platform maintainer
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/29

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| `WP-001-inventory-20260727` | Imported implementation and focused-test inventory | `reports/wp-001-module-test-inventory.md` | Recorded; execution coverage blocked by dependency provisioning |
| `WP-002-retry-capture-20260730` | Bounded idempotent retries, `Retry-After`, transport failure handling, circuit breaking and structured decisions | `src/riopa_provenance/retry.py`, `src/riopa_provenance/capture.py`, `tests/test_retry.py`, `tests/test_capture.py` | Implemented; static/smoke evidence passed, full runtime suite pending dependency provisioning |
| `WP-002-dns-validation-20260730` | Connection-time resolver address validation against private-address/rebinding risks | `src/riopa_provenance/capture.py`, `tests/test_capture.py` | Implemented as policy resolver hook; transport integration and full runtime suite pending |
| `WP-002-source-health-20260730` | Deterministic freshness, change, degradation and disappearance classification | `src/riopa_provenance/health.py`, `schemas/source-health-observation.schema.json`, `tests/test_health.py` | Versioned record implemented; adapter persistence and full runtime suite pending |

## Blocking defects

- None recorded.

## Decisions, exceptions and limitations

- None recorded.

## Review and handover

Required reviewer roles: Provenance reviewer, Security reviewer, Data steward, Operations reviewer, External user reviewer.

This index is deliberately non-assertive while the track remains `specified`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, independently reviewed where required, and sufficient for the applicable release gates.
