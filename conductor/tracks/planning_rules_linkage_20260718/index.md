# Evidence index: Council planning spatial-to-rule linkage

- **Track ID:** `planning_rules_linkage_20260718`
- **Status:** `active`
- **Target release:** `0.6.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Reference`
- **Risk / priority:** `Critical` / `P1`
- **V1 critical:** `yes`
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Spatial data lead
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/74

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| `WP-007-wcc-plan-source-pair-20260731` | One real WCC District Plan zone feature and the official National Planning Standards document are separately preserved | `evidence/wp007-real-slice/manifest.json`, `reports/wp007-bounded-real-slice.md` | Source preservation passes; no provision link, legal interpretation, operative-status assertion or agent-panel-qualified extraction is claimed |
| `PLANNING-IDENTITY-LINKAGE-20260824` | Bounded plan-version, provision and planning-link identity contracts preserve source anchors, uncertainty and non-authority controls | `src/riopa_provenance/planning.py`, `tests/test_planning.py`, `docs/planning-identity-linkage-contract-20260824.json` | Contract and negative tests pass; real council coverage, legal interpretation, geometry linkage, panel qualification and authority remain open |
| `PLANNING-SOURCE-INTAKE-20260825` | Digest-bound declared plan-document, structure and source-anchor intake | `src/riopa_provenance/planning.py:build_plan_source_intake`, `docs/planning-source-intake-contract-20260825.json`, `tests/test_planning.py` | Non-contacting candidate intake passes; actual bytes, preservation, legal status and council-specific evidence remain open |
| `PLANNING-PROVISION-EXTRACTION-20260825` | Provenance-bearing structured/manual/AI-assisted provision extraction record | `src/riopa_provenance/planning.py:build_provision_extraction_record`, `docs/planning-provision-extraction-contract-20260825.json`, `tests/test_planning.py` | Hashes, uncertainty and tool identity are preserved; records remain unreviewed and non-authoritative |
| `PLANNING-FEATURE-PROVISION-LINKAGE-20260825` | Record deterministic links from bounded planning feature references to provision versions without asserting legal effect | `src/riopa_provenance/planning.py:build_feature_provision_linkage`, `docs/planning-feature-provision-linkage-contract-20260825.json`, `tests/test_planning.py` | Contract is tested and promotion-disabled; council payloads, legal interpretation, review and completeness remain open |
| `PLANNING-RULE-STRUCTURE-20260825` | Preserve rule hierarchy, exceptions, combined-rule references and unresolved states without legal interpretation | `src/riopa_provenance/planning.py:build_rule_structure_record`, `docs/planning-rule-structure-contract-20260825.json`, `tests/test_planning.py` | Structure contract is tested and promotion-disabled; source-faithful text, precedence and council validation remain open |
| `PLANNING-CONCEPT-CROSSWALK-20260825` | Preserve original-to-canonical planning concept mappings through the canonical crosswalk contract | `src/riopa_provenance/planning.py:build_planning_concept_crosswalk`, `docs/planning-concept-crosswalk-contract-20260825.json`, `tests/test_planning.py` | Batch contract is tested and promotion-disabled; semantic equivalence, council validation and authority remain open |
| `PLANNING-FEASIBILITY-20260825` | Preserve cited rule statuses, confidence and caveats without reducing feasibility to an unsupported boolean | `src/riopa_provenance/planning.py:build_planning_feasibility_record`, `docs/planning-feasibility-contract-20260825.json`, `tests/test_planning.py` | Conflicts become unresolved and authority is required; legal interpretation, council validation and completeness remain open |
| `PLANNING-TWO-STRUCTURE-VALIDATION-20260825` | Exercise the bounded planning contracts across two structurally different synthetic council-shaped fixtures | `docs/planning-two-structure-validation-20260825.json`, `tests/test_planning_structural_validation.py` | Structural variation validates; real council documents, panel-of-agents review, legal interpretation and authority remain open |
| `PLANNING-VERSIONED-METHODS-20260825` | Publish the bounded versioned-link method sequence and non-authority limitations | `docs/planning-versioned-links-methods-20260825.md`, `tests/test_planning_versioned_methods.py` | Documentation candidate is tested; source capture, panel review, legal interpretation, preservation and authority remain open |
| `PLANNING-LINK-SAMPLE-PANEL-20260825` | Four-lens agent-panel review and bounded error accounting over two structurally different synthetic fixtures | `docs/planning-link-sample-panel-review-20260825.json`, `tests/test_planning_link_sample_panel_review.py` | Synthetic contracts are qualified with unresolved feasibility retained; real council evidence, factual external participation, legal interpretation and authority remain open |
| `PLANNING-LINKAGE-ERROR-LEDGER-20260825` | Fail-closed quantification of missing link targets, crosswalk sources and feasibility provisions | `src/riopa_provenance/planning.py::build_planning_linkage_error_report`, `docs/planning-linkage-error-ledger-20260825.json`, `tests/test_planning_linkage_error_report.py` | Consistent and mutated synthetic packets are measured deterministically; no repair, legal interpretation, completeness or authority claim is made |
| `PLANNING-RULES-CLOSEOUT-20260825` | Link implementation, tests, agent-panel, migration and release-candidate evidence for the bounded planning contract | `docs/planning-rules-closeout-evidence-20260825.json`, `tests/test_planning_closeout_evidence.py` | Repository-owned closeout slice is linked and promotion-disabled; real council bytes, legal authority, external participation and release authority remain open |

The same revision’s Conductor regeneration receipt records the methods hash,
roadmap status, generated issue graph and full quality harness. This closes only
the bookkeeping task; planning authority, national, operational and release
gates remain open (`docs/planning-rules-conductor-regeneration-20260825.json`).

## Blocking defects

- Real council document bytes, source-faithful preservation, legal authority,
  external participation and release-authority evidence remain open.

## Decisions, exceptions and limitations

- The closeout packet records only repository-owned contracts and synthetic
  fixtures. It does not resolve real council, legal or release gates.

## Review and handover

Required agent-panel lenses: Governance analyst, API/schema analyst, Data-governance analyst, Scientific-methods analyst.

This index is deliberately non-assertive while the track remains `active`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, agent-panel qualified where required, and sufficient for the applicable release gates.
