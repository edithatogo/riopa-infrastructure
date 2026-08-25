# Plan: planning_rules_linkage_20260718

## 1. Legal/document identity model

- [x] 1.1 Define plan, plan-version, chapter, provision, citation and legal-status identities. (`src/riopa_provenance/planning.py`, `tests/test_planning.py`, `docs/planning-identity-linkage-contract-20260824.json`; commit `cc384d3`)
- [~] 1.2 Preserve declared official-document, structure and source-anchor records before interpretation. The intake is digest-bound, non-contacting and promotion-disabled; actual document bytes, preservation acceptance and council-specific evidence remain open (`src/riopa_provenance/planning.py:build_plan_source_intake`, `docs/planning-source-intake-contract-20260825.json`, `tests/test_planning.py`).
- [x] 1.3 Define link evidence, confidence, review and uncertainty. (`src/riopa_provenance/planning.py`, `tests/test_planning.py`, `docs/planning-identity-linkage-contract-20260824.json`; commit `cc384d3`)

## 2. Extraction and linkage

- [~] 2.1 Implement structured/manual/AI-assisted provision extraction records with text/input hashes, uncertainty and tool identity. Records remain unreviewed and promotion-disabled; real source extraction, legal interpretation and panel qualification remain open (`src/riopa_provenance/planning.py:build_provision_extraction_record`, `docs/planning-provision-extraction-contract-20260825.json`, `tests/test_planning.py`).
- [ ] 2.2 Link zone, overlay, precinct and designation features to provision versions.
- [ ] 2.3 Represent hierarchy, exceptions, combined rules and unresolved states.

## 3. Crosswalk and feasibility

- [ ] 3.1 Build original-to-canonical planning concept crosswalks.
- [ ] 3.2 Implement cited feasibility queries with status and uncertainty.
- [ ] 3.3 Validate on two structurally different councils.

## 4. Review and stable release

- [ ] 4.1 Conduct independent link sample review and error analysis.
- [ ] 4.2 Resolve or quantify missing/incorrect linkage.
- [ ] 4.3 Publish versioned links, methods and non-authority limitations.

## Track closeout

- [ ] C.1 Link implementation, test, review, migration and release evidence in `index.md`.
- [x] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected. The locked methods generation, roadmap status, issue graph and full quality harness passed; the methods output was temporary and not a release artifact (`docs/planning-rules-conductor-regeneration-20260825.json`).
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [ ] C.4 Update metadata status and target-release evidence through the Conductor workflow.

## Review fixes

- [x] R1 Register the new planning module in the Python 3.14 coverage inventory after hosted CI discovery. (`docs/module-coverage-inventory-20260825.json`; commit `91c584e`)
