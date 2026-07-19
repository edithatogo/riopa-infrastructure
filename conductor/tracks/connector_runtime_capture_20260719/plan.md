# Plan: connector_runtime_capture_20260719

## 1. Runtime contract

- [ ] 1.1 Define adapter lifecycle, capture attempts, idempotency and raw object interfaces.
- [ ] 1.2 Define HTTP/service/document evidence and secret-redaction rules.
- [ ] 1.3 Define rights, governance and publication hooks.

## 2. Adapter implementations

- [ ] 2.1 Implement ArcGIS REST and WFS/OGC adapters.
- [ ] 2.2 Implement Koordinates/API and document/file adapters.
- [ ] 2.3 Implement optional WARC/WACZ web-evidence capture with policy controls.

## 3. Reliability and observability

- [ ] 3.1 Add rate limiting, retries, resume, quarantine and pagination tests.
- [ ] 3.2 Add capability/schema drift detection and source-health events.
- [ ] 3.3 Add metrics, structured logs and diagnostic bundles.

## 4. Real-source validation

- [ ] 4.1 Capture one national and one council/planning source end to end.
- [ ] 4.2 Review security, rights, load and evidence completeness.
- [ ] 4.3 Publish the stable adapter contract and authoring guide.

## Track closeout

- [ ] C.1 Link implementation, test, review, migration and release evidence in `index.md`.
- [ ] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [ ] C.4 Update metadata status and target-release evidence through the Conductor workflow.
