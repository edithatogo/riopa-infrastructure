# Evidence index: Common connector runtime and faithful capture framework

- **Track ID:** `connector_runtime_capture_20260719`
- **Status:** `active`
- **Target release:** `0.4.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Platform`
- **Risk / priority:** `Critical` / `P0`
- **V1 critical:** `yes`

Closeout sequence: `docs/foundation-provenance-connector-ontology-closeout-plan.md`.
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Core platform maintainer
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/29

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| `WP-001-quality-reconciliation-20260731` | Imported implementation, functional-suite and branch-coverage baseline | `reports/quality-baseline-inventory.md` | 467 tests and 93.27% branch-aware coverage pass the unchanged 90% gate locally; hosted exact-head confirmation remains separate |
| `WP-002-retry-capture-20260730` | Bounded idempotent retries, `Retry-After`, transport failure handling, circuit breaking and structured decisions | `src/riopa_provenance/retry.py`, `src/riopa_provenance/capture.py`, `tests/test_retry.py`, `tests/test_capture.py` | Implemented and exercised in the complete functional suite |
| `WP-002-dns-validation-20260731` | Connection-time DNS pinning against private-address/rebinding risks while preserving HTTP Host and TLS SNI | `src/riopa_provenance/capture.py`, `tests/test_capture.py` | Pinned transport and negative rebinding tests implemented |
| `WP-002-source-health-20260730` | Deterministic freshness, change, degradation and disappearance classification | `src/riopa_provenance/health.py`, `schemas/source-health-observation.schema.json`, `tests/test_health.py` | Versioned record implemented and exercised in the complete functional suite |
| `WP-002-capture-observability-20260731` | Runtime attempt, success, failure, byte and failure-category observability | `src/riopa_provenance/capture.py`, `tests/test_capture.py` | Dependency-free metrics and structured failure callback tested |
| `CONNECTOR-RUNTIME-CONTRACT-20260822` | Adapter lifecycle, capture/raw-object, evidence-redaction and rights/publication hook definitions | `src/riopa_provenance/capture.py`, `src/riopa_provenance/retry.py`, `src/riopa_provenance/governance.py`, `src/riopa_provenance/publication.py`, `schemas/source-acquisition-approval.schema.json`, `docs/source-acquisition-runbook.md`, `tests/test_capture.py`, `tests/test_retry.py` | Tasks 1.1–1.3 are reconciled to executable repository contracts; live adapter coverage, real-source validation, external rights and publication gates remain open |
| `CONNECTOR-ADAPTER-CONTRACT-20260824` | ArcGIS REST and WFS/OGC adapter request-shape and deterministic capture safeguards | `src/riopa_provenance/arcgis.py`, `src/riopa_provenance/wfs.py`, `tests/test_arcgis.py`, `tests/test_wfs.py` | HTTPS/no-userinfo preflight, bounded identifiers, deterministic pagination and reconciliation are executable-tested; live-source, rights, publication and external qualification gates remain open |

## Blocking defects

- None recorded.

## Decisions, exceptions and limitations

- None recorded.

## Review and handover

Required agent-panel lenses: Provenance analyst, Security analyst, Data-governance analyst, Operations analyst, External-user workflow analyst.

This index is deliberately non-assertive while the track remains `specified`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, agent-panel qualified where required, and sufficient for the applicable release gates.
