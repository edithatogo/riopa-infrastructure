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
| `CONNECTOR-KOORDINATES-DOWNLOAD-CONTRACT-20260824` | Koordinates export/download URL preflight and redirect-safe evidence | `src/riopa_provenance/linz_export.py`, `tests/test_linz_export.py` | HTTPS/no-userinfo preflight and exact export/job/download capture are executable-tested; live-source, rights, publication and external qualification gates remain open |
| `CONNECTOR-WARC-WACZ-PACKAGING-20260824` | Policy-controlled offline WARC/WACZ packaging of verified captures | `src/riopa_provenance/web_archive.py`, `tests/test_web_archive.py` | Deterministic single-record package and negative policy/integrity tests pass; no live web capture, rights/publication, preservation or external qualification is claimed |
| `CONNECTOR-RELIABILITY-CONTROLS-20260824` | Rate limiting and immutable quarantine controls around captured evidence | `src/riopa_provenance/retry.py`, `src/riopa_provenance/capture.py`, `src/riopa_provenance/quarantine.py`, `tests/test_retry.py`, `tests/test_capture.py`, `tests/test_quarantine.py` | Token-bucket delay, bounded retries, and digest-bound quarantine records are executable-tested; hosted long-running operation, real-source and external qualification remain open |
| `CONNECTOR-CAPABILITY-DRIFT-20260824` | Digest-bound capability/schema drift comparison and source-health classification | `src/riopa_provenance/health.py`, `tests/test_health.py` | Added/removed/changed capability fields and stable snapshot digests are executable-tested; live monitoring, alert delivery and external qualification remain open |
| `CONNECTOR-DIAGNOSTIC-BUNDLES-20260824` | Redacted immutable metrics/failure diagnostic bundles | `src/riopa_provenance/diagnostics.py`, `tests/test_diagnostics.py`, `src/riopa_provenance/capture.py`, `tests/test_capture.py` | Recursive redaction, structured failures, digest binding and no-overwrite protection are executable-tested; hosted aggregation and operational alert delivery remain open |
| `CONNECTOR-AUTHORING-GUIDE-20260824` | Bounded adapter contract and authoring guide | `docs/connector-adapter-authoring-guide-20260824.md`, `docs/connector-adapter-contract-20260824.json` | Implemented surfaces and required controls are documented; guide is explicitly non-authorizing and live-source/stable qualification remains pending |

## Blocking defects

- Live national and council/planning capture, rights/publication qualification,
  preservation acceptance, hosted long-running operation, alert delivery and
  external reproduction remain open.

## Repository-owned closeout slice (2026-08-24)

The adapter request contracts, offline WARC/WACZ packaging, rate limiting,
quarantine, capability drift and diagnostic bundle controls are linked above
and validated by `bash scripts/ci_quality.sh` at protected `main` revision
`ed69976d815f064843c3492fa2045807381857ca`. These are repository-owned
contracts and offline safeguards; they do not claim live-source acquisition,
rights clearance, preservation acceptance or operational qualification.

The next implementation boundary is the real-source vertical slice. It must
remain bounded, public-source-only, content-addressed and fail closed until
source rights, load limits, publication scope and hosted credentials are
available. No unsupported national, network, timetable, facility, clinical or
dispatch claim is enabled here.

## Decisions, exceptions and limitations

- This is a single-developer repository. Agent-panel lenses may assess
  packets, but cannot substitute for factual external operator/user evidence,
  hosted execution or accountable release-authority approval.
- Offline fixtures and deterministic packaging are not live-source evidence.
- Missing rights, source status, hosted receipts or participant evidence are
  pending rather than negative evidence.

## Review and handover

Required agent-panel lenses: Provenance analyst, Security analyst, Data-governance analyst, Operations analyst, External-user workflow analyst.

This index is deliberately non-assertive while the track remains `active` at
M1. Status may advance only through `conductor/workflow.md`; evidence must be
immutable or version-addressed, agent-panel qualified where required, and
sufficient for the applicable release gates.
