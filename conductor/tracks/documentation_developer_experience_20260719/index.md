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

The repository-owned progress/reporting increment is tracked in task 2.4.
`docs/repository-progress-reporting-20260831.md` documents the read-only command;
`docs/work-package-reconciliation-20260831.json` separates portable implementation
dispositions from qualification. Tested Tasman archive queries are documented in
`docs/tasman-verified-query-examples-20260831.md`. These improvements do not
qualify a release-candidate user/operator journey or promote this track.

Three isolated advisory subagents implemented and cross-reviewed the queue,
archive disposition, query examples and ledger; the parent integrated reporting
and reviewed evidence. The final focused group passes 73 tests. The broad local
run passes 1,706 tests with one skip and 90.41% branch-aware coverage; the later
ledger-baseline test and final reporter checks also pass separately. Strict
MyPy/Bandit and reproducibility pass. An initial packaging output-path failure
was isolated from the passing SBOM generation; the complete sequential quality
rerun passes. Hosted CI remains separately recorded at integration. No human participant, release approval, new acquisition
or scheduled execution is asserted by this repository-owned increment.

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| `DOCS-IA-CONTRACT-20260824` | Audience, workflow, interface and normative-source inventory | `docs/documentation-information-architecture-20260824.md`, `docs/documentation-contract-20260824.json` | Contract is repository-owned and bounded; external usability evidence remains open |
| `DOCS-TUTORIAL-CONVENTIONS-20260824` | Executable tutorial, example, accessibility and safety conventions | `docs/tutorial-and-example-conventions-20260824.md`, `tests/test_documentation_contract.py` | Contract and negative scope controls pass locally; user/operator studies and RC execution remain open |
| `DOCS-HOSTED-AGENT-WORKFLOWS-20260825` | Protected-main agent-user-workflows rehearsal | [GitHub Actions run 32739643452](https://github.com/edithatogo/riopa-infrastructure/actions/runs/32739643452), `docs/evidence-campaign-status-20260821.json` | Passed on exact revision `88f5376`; the bounded rehearsal does not establish the later exact stable-candidate role-separated journeys |
| `DOCS-INVENTORY-SAFETY-20260825` | Audience/workflow inventory, normative map, tutorial controls and bounded safety review | `docs/documentation-information-architecture-20260824.md`, `docs/documentation-contract-20260824.json`, `docs/documentation-inventory-and-safety-review-20260825.json`, `tests/test_documentation_inventory_review.py` | Repository-owned documentation baseline is qualified for bounded scope; owner-authorized agent-operated user/operator journeys, release-candidate and authority gates remain open |
| `DOCUMENTATION-USAGE-GUIDES-20260825` | User, operator, contributor, maintainer and migration handoff is explicit and scope-bounded | `docs/usage-guides-20260825.md`, `tests/test_usage_guides.py` | Repository-owned guide contract passes; external usability, RC execution and publication remain open |
| `DOCUMENTATION-REFERENCE-INDEX-20260825` | API, CLI, schema and ontology surfaces are versioned and discoverable | `docs/reference-index-20260825.json`, `tests/test_reference_index.py` | Deterministic repository reference index passes; external usability and publication remain open |
| `DOCUMENTATION-TUTORIAL-20260825` | Public/synthetic end-to-end tutorial includes positive and fail-closed troubleshooting paths | `docs/bounded-lineage-tutorial-20260825.md`, `scripts/run_bounded_lineage_tutorial.py`, `tests/test_bounded_lineage_tutorial.py` | Offline synthetic rehearsal passes; external usability, RC execution and publication remain open |
| `DOCUMENTATION-FRICTION-20260825` | Anticipated friction and support-burden register with mitigations | `docs/documentation-friction-register-20260825.json`, `tests/test_documentation_friction_register.py` | Repository analysis is recorded; owner-authorized agent-operated user/operator journeys, accessibility, RC and authority gates remain open |
| `DOCUMENTATION-SUPPORT-20260825` | Preview support channels, triage priorities, single-developer ownership and sustainability bounds | `docs/documentation-support-readiness-20260825.json`, `tests/test_documentation_support_readiness.py` | Preview contract is recorded; stable support, external participation, RC soak, preservation and authority gates remain open |
| `DOCUMENTATION-ARCHIVE-CANDIDATE-20260825` | Content-addressed versioned documentation archive candidate | `scripts/build_documentation_archive_manifest.py`, `docs/documentation-archive-manifest-20260825.json`, `tests/test_documentation_archive_manifest.py` | Local manifest is deterministic and unpublished; RC execution, external usability, preservation acceptance, publication and authority gates remain open |
| `DOCUMENTATION-CANDIDATE-TUTORIAL-REHEARSAL-20260825` | Execute every registered tutorial against one exact repository candidate revision | `scripts/run_release_candidate_tutorials.py`, `tests/test_release_candidate_tutorials.py` | Bounded repository rehearsal passes; it is not RC promotion evidence and does not replace owner-authorized agent-operated user/operator journeys or elapsed soak |
| `DOCUMENTATION-AGENT-WORKFLOW-REPORT-VALIDATION-20260829` | Validate the bounded owner-authorized agent workflow report shape and nonclaims | `scripts/validate_agent_user_workflow_report.py`, `tests/test_agent_user_workflow_report_validator.py`, `docs/documentation-agent-workflow-report-validation-20260829.json` | Report shape is machine-checked; factual external participant, exact stable-candidate and release-authority gates remain open |
| `DOCUMENTATION-CLOSEOUT-EVIDENCE-20260825` | Link implementation, tests, review, migration and release-candidate rehearsal evidence for the repository-owned slice | `docs/documentation-closeout-evidence-20260825.json`, `tests/test_documentation_closeout_evidence.py` | Evidence categories are linked and fail-closed; external usability, preservation acceptance, elapsed soak and release-authority gates remain open |
| `DOCUMENTATION-ISSUE-SYNC-20260830` | Generated Conductor phase projections are synchronized to GitHub issues #125–#128 with content digests | `docs/documentation-issue-sync-20260830.json`, `project/issues.yaml` | Descriptions synchronized; external usability, preservation, soak, promotion and authority gates remain open |
| `DOCUMENTATION-ISSUE-SYNC-RECEIPT-V2-20260830` | CLI-output receipt records the deployed GitHub issue body digests without mutating the original local-source receipt | `docs/documentation-issue-sync-20260830-receipt-v2.json` | Remote bodies verified; no external usability, preservation, soak, promotion or authority gate is closed |

## Blocking defects

- User/operator workflow studies, accessibility/terminology review, release-
  candidate tutorial execution, support ownership and versioned publication
  remain open.

## Repository-owned closeout slice (2026-08-24)

The information architecture and tutorial conventions are validated by
`bash scripts/ci_quality.sh` at protected `main` revision
`ed69976d815f064843c3492fa2045807381857ca`. They establish documentation
contracts and safety boundaries, not user-study, agent-operator journey or release
evidence.

The 2026-08-25 closeout packet links implementation, test, review, migration and
release-candidate rehearsal evidence for the same bounded slice. Its release
references remain an unpublished candidate and do not advance the track beyond
M1.

The same revision’s Conductor regeneration receipt records the methods hash,
roadmap status, generated issue graph and full quality harness. This closes only
the bookkeeping task; it does not substitute for agent-user, agent-operator or
release-authority evidence (`docs/documentation-conductor-regeneration-20260825.json`).

## Decisions, exceptions and limitations

- This is a single-developer repository. General panel review does not by itself
  establish a candidate-bound role-separated journey; each required journey
  must be executed and content-bound.
- Tutorials remain public/synthetic and non-operational until separately
  evidenced.

## Review and handover

PR #763's initial hosted CI run `33353850937` passed 1,707 tests with one skip
and 90.41% branch-aware coverage. A subsequent automated review identified
summary-to-receipt semantic drift; the reporter now binds the projected claims
and unchanged qualification limits to the parsed acceptance receipts. Its fix
is covered by adversarial mutation tests and a separate isolated subagent review.
The questioned implementation revision `f145368` was independently confirmed
as the parent of reviewed revision `c22df71` through local Git and GitHub metadata.
These are bounded reporting corrections, not publication or track qualification.

Required agent-panel lenses: User-workflow analyst, API/schema analyst, Research-object analyst, Operations analyst, Interoperability analyst, Governance analyst.

This index is deliberately non-assertive while the track remains `active` at
M1. Status may advance only through `conductor/workflow.md`; evidence must be
immutable or version-addressed, agent-panel qualified where required, and
sufficient for the applicable release gates.
