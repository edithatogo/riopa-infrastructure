# Plan: connector_runtime_capture_20260719

## 1. Runtime contract

- [x] 1.1 Define adapter lifecycle, capture attempts, idempotency and raw object interfaces. Evidence: `src/riopa_provenance/capture.py`, `src/riopa_provenance/retry.py`, `tests/test_capture.py`, `tests/test_retry.py`. (ad5aef7)
- [x] 1.2 Define HTTP/service/document evidence and secret-redaction rules. Evidence: `src/riopa_provenance/capture.py::CapturePolicy`, `redact_url`, `redact_text`, `tests/test_capture.py`, `docs/source-acquisition-runbook.md`. (ad5aef7)
- [x] 1.3 Define rights, governance and publication hooks. Evidence: `schemas/source-acquisition-approval.schema.json`, `src/riopa_provenance/governance.py`, `src/riopa_provenance/publication.py`, `docs/source-acquisition-runbook.md`. (ad5aef7)

## 2. Adapter implementations

- [~] 2.1 Implement ArcGIS REST and WFS/OGC adapters. Existing archivers now enforce HTTPS/no-userinfo request contracts before capture, deterministic pagination, count/identity reconciliation and redaction. Evidence: `src/riopa_provenance/arcgis.py`, `src/riopa_provenance/wfs.py`, `tests/test_arcgis.py`, `tests/test_wfs.py`; live-source acceptance, rights/publication qualification and national/council capture remain pending.
- [~] 2.2 Implement Koordinates/API and document/file adapters. Existing Koordinates export archival now rejects unsafe initial download URLs before redirect capture and preserves exact export/job/download evidence. Evidence: `src/riopa_provenance/linz_export.py`, `tests/test_linz_export.py`; live-source acceptance, rights/publication qualification and external reproduction remain pending.
- [~] 2.3 Implement optional WARC/WACZ web-evidence capture with policy controls. Offline packaging of verified content-addressed captures is implemented with deterministic WARC/WACZ output and fail-closed URL, secret, size, policy and digest checks. Evidence: `src/riopa_provenance/web_archive.py`, `tests/test_web_archive.py`; live web capture, rights/publication, preservation and external qualification remain pending. (04ea0f7)

### Review fixes

- [x] Prevent overwriting an existing WACZ evidence file and add an immutability regression test. (`107f347`)

## 3. Reliability and observability

- [~] 3.1 Add rate limiting, retries, resume, quarantine and pagination tests. Existing bounded retry/resume/pagination contracts are now supplemented by an injected token-bucket limiter in `HttpCaptureClient` and immutable digest-bound quarantine records. Evidence: `src/riopa_provenance/retry.py`, `src/riopa_provenance/capture.py`, `src/riopa_provenance/quarantine.py`, `tests/test_retry.py`, `tests/test_capture.py`, `tests/test_quarantine.py`; hosted long-running operation and real-source qualification remain pending. (f0f9d1a)
- [~] 3.2 Add capability/schema drift detection and source-health events. Added digest-bound, field-specific capability drift records alongside the existing source-health observation contract. Evidence: `src/riopa_provenance/health.py`, `tests/test_health.py`; source-specific live monitoring and hosted alert delivery remain pending. (18ab881)
- [~] 3.3 Add metrics, structured logs and diagnostic bundles. Existing metrics/failure callbacks are now serializable into immutable diagnostic bundles with recursive redaction and no-overwrite protection. Evidence: `src/riopa_provenance/capture.py`, `src/riopa_provenance/diagnostics.py`, `tests/test_capture.py`, `tests/test_diagnostics.py`; hosted log aggregation and operational alert delivery remain pending. (0ebf57f; review fix 354aba3)

## 4. Real-source validation

- [ ] 4.1 Capture one national and one council/planning source end to end.
- [ ] 4.2 Review security, rights, load and evidence completeness.
- [ ] 4.3 Publish the stable adapter contract and authoring guide.

## Track closeout

- [ ] C.1 Link implementation, test, review, migration and release evidence in `index.md`.
- [ ] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [ ] C.4 Update metadata status and target-release evidence through the Conductor workflow.
