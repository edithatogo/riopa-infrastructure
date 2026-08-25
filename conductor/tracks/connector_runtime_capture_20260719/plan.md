# Plan: connector_runtime_capture_20260719

## 1. Runtime contract

- [x] 1.1 Define adapter lifecycle, capture attempts, idempotency and raw object interfaces. Evidence: `src/riopa_provenance/capture.py`, `src/riopa_provenance/retry.py`, `tests/test_capture.py`, `tests/test_retry.py`. (ad5aef7)
- [x] 1.2 Define HTTP/service/document evidence and secret-redaction rules. Evidence: `src/riopa_provenance/capture.py::CapturePolicy`, `redact_url`, `redact_text`, `tests/test_capture.py`, `docs/source-acquisition-runbook.md`. (ad5aef7)
- [x] 1.3 Define rights, governance and publication hooks. Evidence: `schemas/source-acquisition-approval.schema.json`, `src/riopa_provenance/governance.py`, `src/riopa_provenance/publication.py`, `docs/source-acquisition-runbook.md`. (ad5aef7)

## 2. Adapter implementations

- [x] 2.1 Implement bounded ArcGIS REST and WFS/OGC adapter safeguards. HTTPS/no-userinfo request contracts, deterministic pagination, count/identity reconciliation and redaction are executable-tested; live-source acceptance, rights/publication qualification and national/council capture remain pending. Evidence: `src/riopa_provenance/arcgis.py`, `src/riopa_provenance/wfs.py`, `tests/test_arcgis.py`, `tests/test_wfs.py`.
- [x] 2.2 Implement bounded Koordinates/API and document/file adapter safeguards. Unsafe initial download URLs are rejected before redirect capture and exact export/job/download evidence is preserved; live-source acceptance, rights/publication qualification and external reproduction remain pending. Evidence: `src/riopa_provenance/linz_export.py`, `tests/test_linz_export.py`.
- [x] 2.3 Implement bounded optional WARC/WACZ web-evidence packaging with policy controls. Offline packaging of verified content-addressed captures is deterministic and fail-closed on URL, secret, size, policy and digest checks; live capture, rights/publication, preservation and external qualification remain pending. Evidence: `src/riopa_provenance/web_archive.py`, `tests/test_web_archive.py`. (04ea0f7)

### Review fixes

- [x] Prevent overwriting an existing WACZ evidence file and add an immutability regression test. (`107f347`)

## 3. Reliability and observability

- [x] 3.1 Add rate limiting, retries, resume, quarantine and pagination tests. Existing bounded retry/resume/pagination contracts are supplemented by an injected token-bucket limiter in `HttpCaptureClient` and immutable digest-bound quarantine records. Evidence: `src/riopa_provenance/retry.py`, `src/riopa_provenance/capture.py`, `src/riopa_provenance/quarantine.py`, `tests/test_retry.py`, `tests/test_capture.py`, `tests/test_quarantine.py`; hosted long-running operation and real-source qualification remain pending. (f0f9d1a)
- [x] 3.2 Add capability/schema drift detection and source-health events. Digest-bound, field-specific capability drift records and the source-health observation contract are executable-tested. Evidence: `src/riopa_provenance/health.py`, `tests/test_health.py`; source-specific live monitoring and hosted alert delivery remain pending. (18ab881)
- [x] 3.3 Add metrics, structured logs and diagnostic bundles. Metrics/failure callbacks serialize into immutable diagnostic bundles with recursive redaction and no-overwrite protection. Evidence: `src/riopa_provenance/capture.py`, `src/riopa_provenance/diagnostics.py`, `tests/test_capture.py`, `tests/test_diagnostics.py`; hosted log aggregation and operational alert delivery remain pending. (0ebf57f; review fix 354aba3)

## 4. Real-source validation

- [ ] 4.1 Capture one national and one council/planning source end to end.
- [x] 4.2 Conduct the repository-owned security, rights, load and evidence-completeness review through a bounded four-lens agent panel. The packet and deterministic checks are repository-owned evidence; live-source capture, rights/publication, preservation, hosted monitoring and external participant gates remain open (`docs/connector-panel-qualification-20260825.json`, `tests/test_connector_panel_qualification.py`).
- [x] 4.3 Publish the bounded adapter contract and authoring guide. `docs/connector-adapter-authoring-guide-20260824.md` and `docs/connector-adapter-contract-20260824.json` describe the implemented surfaces and controls without claiming stable production qualification; live-source, rights/publication, preservation and external gates remain pending. (`tests/test_connector_authoring_contract.py`)

## Track closeout

- [x] C.1 Link implementation, test, review, migration and release evidence in `index.md` for the repository-owned contract slice; live-source and external gates remain explicitly pending.
- [x] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [x] C.4 Update metadata status and target-release evidence through the Conductor workflow; status remains `active`/M1 because the documented gates are unresolved.
