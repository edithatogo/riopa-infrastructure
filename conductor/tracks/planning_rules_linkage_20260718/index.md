# Evidence index: Council planning spatial-to-rule linkage

- **Track ID:** `planning_rules_linkage_20260718`
- **Status:** `specified`
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

The same revision’s Conductor regeneration receipt records the methods hash,
roadmap status, generated issue graph and full quality harness. This closes only
the bookkeeping task; planning authority, national, operational and release
gates remain open (`docs/planning-rules-conductor-regeneration-20260825.json`).

## Blocking defects

- None recorded.

## Decisions, exceptions and limitations

- None recorded.

## Review and handover

Required agent-panel lenses: Governance analyst, API/schema analyst, Data-governance analyst, Scientific-methods analyst.

This index is deliberately non-assertive while the track remains `active`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, agent-panel qualified where required, and sufficient for the applicable release gates.
