# Plan: planning_rules_linkage_20260718

## 1. Legal/document identity model

- [x] 1.1 Define plan, plan-version, chapter, provision, citation and legal-status identities. (`src/riopa_provenance/planning.py`, `tests/test_planning.py`, `docs/planning-identity-linkage-contract-20260824.json`; commit `cc384d3`)
- [x] 1.2 Preserve declared official-document, structure and source-anchor records before interpretation. The intake is digest-bound, non-contacting and promotion-disabled; actual document bytes, preservation acceptance and council-specific evidence remain open (`src/riopa_provenance/planning.py:build_plan_source_intake`, `docs/planning-source-intake-contract-20260825.json`, `tests/test_planning.py`).
- [x] 1.3 Define link evidence, confidence, review and uncertainty. (`src/riopa_provenance/planning.py`, `tests/test_planning.py`, `docs/planning-identity-linkage-contract-20260824.json`; commit `cc384d3`)

## 2. Extraction and linkage

- [x] 2.1 Implement structured/manual/AI-assisted provision extraction records with text/input hashes, uncertainty and tool identity. Records remain unreviewed and promotion-disabled; real source extraction, legal interpretation and panel qualification remain open (`src/riopa_provenance/planning.py:build_provision_extraction_record`, `docs/planning-provision-extraction-contract-20260825.json`, `tests/test_planning.py`).
- [x] 2.2 Record digest-bound links from zone, overlay, precinct and designation feature references to provision versions without legal interpretation (`src/riopa_provenance/planning.py:build_feature_provision_linkage`, `docs/planning-feature-provision-linkage-contract-20260825.json`, `tests/test_planning.py`). Real council payloads, authority and linkage review remain open.
- [x] 2.3 Preserve hierarchy, exception, combined-rule and unresolved-state references without legal interpretation (`src/riopa_provenance/planning.py:build_rule_structure_record`, `docs/planning-rule-structure-contract-20260825.json`, `tests/test_planning.py`). Source-faithful text, precedence, council validation and panel review remain open.

## 3. Crosswalk and feasibility

- [x] 3.1 Build digest-bound original-to-canonical planning concept crosswalk records using the canonical contract (`src/riopa_provenance/planning.py:build_planning_concept_crosswalk`, `docs/planning-concept-crosswalk-contract-20260825.json`, `tests/test_planning.py`). Source-faithful council records, semantic review and authority remain open.
- [x] 3.2 Implement cited feasibility records that retain rule sources, status, confidence and caveats, and fail closed on conflicts (`src/riopa_provenance/planning.py:build_planning_feasibility_record`, `docs/planning-feasibility-contract-20260825.json`, `tests/test_planning.py`). Legal interpretation, council validation and authority remain open.
- [x] 3.3 Validate the bounded intake, structure, linkage, crosswalk and feasibility contracts on two structurally different synthetic council-shaped fixtures (`docs/planning-two-structure-validation-20260825.json`, `tests/test_planning_structural_validation.py`). Real council documents, panel-of-agents review, legal interpretation and authority remain open.

## 4. Review and stable release

- [x] 4.1 Conduct a panel-of-agents link sample review and bounded error analysis over the two synthetic council-shaped fixtures (`docs/planning-link-sample-panel-review-20260825.json`, `tests/test_planning_link_sample_panel_review.py`). Factual external participation, real council evidence, legal interpretation and authority remain open.
- [x] 4.2 Quantify missing or incorrect references without inferring repairs (`src/riopa_provenance/planning.py::build_planning_linkage_error_report`, `docs/planning-linkage-error-ledger-20260825.json`, `tests/test_planning_linkage_error_report.py`). Real council completeness, legal interpretation and authority remain open.
- [x] 4.3 Publish the bounded versioned-link methods and non-authority limitations (`docs/planning-versioned-links-methods-20260825.md`, `tests/test_planning_versioned_methods.py`). Panel-of-agents review, real source capture, legal interpretation, preservation and authority remain open.

## Track closeout

- [x] C.1 Link implementation, test, agent-panel, migration and release evidence in `index.md` for the repository-owned bounded slice (`docs/planning-rules-closeout-evidence-20260825.json`, `tests/test_planning_closeout_evidence.py`). Real council, legal-authority, external-participation and release gates remain open.
- [x] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected. The locked methods generation, roadmap status, issue graph and full quality harness passed; the methods output was temporary and not a release artifact (`docs/planning-rules-conductor-regeneration-20260825.json`).
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [x] C.4 Update metadata status and target-release evidence through the Conductor workflow; metadata remains `active`/M1 for target release `0.6.0`, with real council-source capture, legal interpretation, external participation, preservation and accountable-authority gates unresolved.

## Review fixes

- [x] R1 Register the new planning module in the Python 3.14 coverage inventory after hosted CI discovery. (`docs/module-coverage-inventory-20260825.json`; commit `91c584e`)
- [x] R2 Reconcile the evidence index status and blocking-defect register with the active metadata and the bounded closeout packet (`docs/planning-rules-closeout-evidence-20260825.json`).
