# Evidence index: Documentation, developer experience and user support readiness

- **Track ID:** `documentation_developer_experience_20260719`
- **Status:** `active`
- **Target release:** `0.9.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Platform`
- **Risk / priority:** `High` / `P0`
- **V1 critical:** `yes`
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Publication and validation lead
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/124

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| `DOCS-IA-CONTRACT-20260824` | Audience, workflow, interface and normative-source inventory | `docs/documentation-information-architecture-20260824.md`, `docs/documentation-contract-20260824.json` | Contract is repository-owned and bounded; external usability evidence remains open |
| `DOCS-TUTORIAL-CONVENTIONS-20260824` | Executable tutorial, example, accessibility and safety conventions | `docs/tutorial-and-example-conventions-20260824.md`, `tests/test_documentation_contract.py` | Contract and negative scope controls pass locally; user/operator studies and RC execution remain open |
| `DOCS-HOSTED-AGENT-WORKFLOWS-20260825` | Protected-main agent-user-workflows rehearsal | [GitHub Actions run 32739643452](https://github.com/edithatogo/riopa-infrastructure/actions/runs/32739643452), `docs/evidence-campaign-status-20260821.json` | Passed on exact revision `88f5376`; agent rehearsal is bounded evidence and cannot substitute for factual external user/operator participation |
| `DOCS-INVENTORY-SAFETY-20260825` | Audience/workflow inventory, normative map, tutorial controls and bounded safety review | `docs/documentation-information-architecture-20260824.md`, `docs/documentation-contract-20260824.json`, `docs/documentation-inventory-and-safety-review-20260825.json`, `tests/test_documentation_inventory_review.py` | Repository-owned documentation baseline is qualified for bounded scope; external user/operator, release-candidate and authority gates remain open |
| `DOCUMENTATION-USAGE-GUIDES-20260825` | User, operator, contributor, maintainer and migration handoff is explicit and scope-bounded | `docs/usage-guides-20260825.md`, `tests/test_usage_guides.py` | Repository-owned guide contract passes; external usability, RC execution and publication remain open |
| `DOCUMENTATION-REFERENCE-INDEX-20260825` | API, CLI, schema and ontology surfaces are versioned and discoverable | `docs/reference-index-20260825.json`, `tests/test_reference_index.py` | Deterministic repository reference index passes; external usability and publication remain open |
| `DOCUMENTATION-TUTORIAL-20260825` | Public/synthetic end-to-end tutorial includes positive and fail-closed troubleshooting paths | `docs/bounded-lineage-tutorial-20260825.md`, `scripts/run_bounded_lineage_tutorial.py`, `tests/test_bounded_lineage_tutorial.py` | Offline synthetic rehearsal passes; external usability, RC execution and publication remain open |
| `DOCUMENTATION-FRICTION-20260825` | Anticipated friction and support-burden register with mitigations | `docs/documentation-friction-register-20260825.json`, `tests/test_documentation_friction_register.py` | Repository analysis is recorded; external user/operator, accessibility, RC and authority gates remain open |
| `DOCUMENTATION-SUPPORT-20260825` | Preview support channels, triage priorities, single-developer ownership and sustainability bounds | `docs/documentation-support-readiness-20260825.json`, `tests/test_documentation_support_readiness.py` | Preview contract is recorded; stable support, external participation, RC soak, preservation and authority gates remain open |
| `DOCUMENTATION-ARCHIVE-CANDIDATE-20260825` | Content-addressed versioned documentation archive candidate | `scripts/build_documentation_archive_manifest.py`, `docs/documentation-archive-manifest-20260825.json`, `tests/test_documentation_archive_manifest.py` | Local manifest is deterministic and unpublished; RC execution, external usability, preservation acceptance, publication and authority gates remain open |
| `DOCUMENTATION-CANDIDATE-TUTORIAL-REHEARSAL-20260825` | Execute every registered tutorial against one exact repository candidate revision | `scripts/run_release_candidate_tutorials.py`, `tests/test_release_candidate_tutorials.py` | Bounded repository rehearsal passes; it is not RC promotion evidence and does not replace external user/operator participation or elapsed soak |
| `DOCUMENTATION-CLOSEOUT-EVIDENCE-20260825` | Link implementation, tests, review, migration and release-candidate rehearsal evidence for the repository-owned slice | `docs/documentation-closeout-evidence-20260825.json`, `tests/test_documentation_closeout_evidence.py` | Evidence categories are linked and fail-closed; external usability, preservation acceptance, elapsed soak and release-authority gates remain open |

## Blocking defects

- User/operator workflow studies, accessibility/terminology review, release-
  candidate tutorial execution, support ownership and versioned publication
  remain open.

## Repository-owned closeout slice (2026-08-24)

The information architecture and tutorial conventions are validated by
`bash scripts/ci_quality.sh` at protected `main` revision
`ed69976d815f064843c3492fa2045807381857ca`. They establish documentation
contracts and safety boundaries, not user-study, external-operator or release
evidence.

The 2026-08-25 closeout packet links implementation, test, review, migration and
release-candidate rehearsal evidence for the same bounded slice. Its release
references remain an unpublished candidate and do not advance the track beyond
M1.

The same revision’s Conductor regeneration receipt records the methods hash,
roadmap status, generated issue graph and full quality harness. This closes only
the bookkeeping task; it does not substitute for external-user, operator or
release-authority evidence (`docs/documentation-conductor-regeneration-20260825.json`).

## Decisions, exceptions and limitations

- This is a single-developer repository. Agent panels may assess documents,
  but cannot substitute for factual external user/operator participation.
- Tutorials remain public/synthetic and non-operational until separately
  evidenced.

## Review and handover

Required agent-panel lenses: External-user workflow analyst, API/schema analyst, Research-object analyst, Operations analyst, Interoperability analyst, Governance analyst.

This index is deliberately non-assertive while the track remains `active` at
M1. Status may advance only through `conductor/workflow.md`; evidence must be
immutable or version-addressed, agent-panel qualified where required, and
sufficient for the applicable release gates.
