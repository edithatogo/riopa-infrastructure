# Plan: publication_validation_20260718

## 1. Validation protocol

- [x] 1.1 Define agent-panel conformance, clean-room and agent-user workflow protocols. Evidence: `docs/single-developer-agent-panel-review-policy.md`, `docs/independent-reproduction-protocol.md`, `docs/release-gate-evidence-matrix.md`, `tests/test_hosted_evidence.py`.
- [ ] 1.2 Define claim-to-evidence and exploratory/confirmatory classifications.
- [ ] 1.3 Select agent-panel validators, environments and analyst-independence criteria.

## 2. Release and citation packages

- [ ] 2.1 Coordinate immutable software, schema, ontology, data, model and research-object versions.
- [ ] 2.2 Generate DOI-ready metadata, citation, provenance, SBOM, attestations and preservation records.
- [ ] 2.3 Verify discovery, install, query, reproduce and cite workflows.

## 3. Agent reproduction

- [ ] 3.1 Reproduce one real-data archive release with an owner-authorized agent.
- [ ] 3.2 Reproduce one applied benchmark with an owner-authorized agent.
- [ ] 3.3 Resolve findings and publish deviations/limitations.

## 4. Publications and correction

- [ ] 4.1 Complete infrastructure/methods, data descriptor and applied publication packages.
- [~] 4.2 Exercise correction, supersession and downstream-impact notification. Bounded package validation is executable; production downstream notification remains open. (`validate_correction_package`, tests)
- [ ] 4.3 Publish validation evidence and stable citation guidance.

## 5. Bounded agent-panel preparation

- [x] 5.1 Define the WP-010 clean-room procedure, independence criteria and content-bound evidence record. (37510dd)
- [x] 5.2 Define the staged Software Heritage plus artifact-repository preservation sequence without claiming a deposit. (37510dd)
- [x] 5.3 Execute three isolated agent lenses across all 28 tracks and publish the fail-closed orchestrator synthesis. (`docs/panel-reports/20260802/manifest.json`)

## Track closeout

- [ ] C.1 Link implementation, test, review, migration and release evidence in `index.md`.
- [ ] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [ ] C.4 Update metadata status and target-release evidence through the Conductor workflow.
