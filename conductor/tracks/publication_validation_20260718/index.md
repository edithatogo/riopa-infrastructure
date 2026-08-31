# Evidence index: Independent validation, release and publication programme

- **Track ID:** `publication_validation_20260718`
- **Status:** `active`
- **Target release:** `0.9.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Reference`
- **Risk / priority:** `High` / `P1`
- **V1 critical:** `yes`
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Publication and validation lead
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/129

## Evidence register

`docs/publication-journal-recovery-20260831.md` records the WP-003 restored-state
and safe-staging increment. The pure journal rejects corrupt or contradictory
checkpoints and supplied receipt hashes before replay; staging preserves existing
directories. The implementation and sentinel/failure/recovery tests are in
`src/riopa_provenance/publication.py`, `tests/test_publication.py` and
`tests/test_publication_staging_safety.py`. This does not establish provider
acceptance or close WP-003's generalized multi-target execution requirements.

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| `WP-003-resumable-publication-20260731` | GitHub, Hugging Face and Zenodo publication steps are resumable, idempotent and conflict-safe | `src/riopa_provenance/publication.py`, `tests/test_publication.py`, `docs/publication-state.md` | Pure state and receipt reconciliation tests pass; no remote publication performed |
| `PUB-RECEIPT-RECONCILIATION-20260825` | Multi-target receipt batches reconcile deterministically and fail closed on replay conflicts | `src/riopa_provenance/publication.py::reconcile_publication_receipts`, `docs/publication-receipt-reconciliation-contract-20260825.json`, `tests/test_publication.py` | Repository-owned contract passes; remote upload/deposit, target acceptance, preservation and authority remain open |
| `WP-006-prepublication-attestation-check-20260731` | GitHub release creation is gated on successful verification of every registered artifact attestation | `.github/workflows/release.yml`, `docs/conformance-and-release-verification.md` | Workflow configured and policy-valid; no release, isolated role-separated clean-room agent reproduction or independent validation is claimed |
| `WP-010-reviewer-ready-synthetic-benchmark-20260801` | A fixed benchmark and standard-library verifier provide a bounded clean-room exercise | `examples/wp010-synthetic-benchmark/`, `scripts/build_wp010_reviewer_bundle.py`, `tests/test_wp010_benchmark.py` | Repository-owned reproduction and the content-bound all-track agent panel pass as bounded evidence; additional agent reproduction remains pending |
| `WP-010-agent-reproduction-protocol-20260801` | Clean-room environment, result and content-binding requirements are explicit for owner-authorized agent execution | `docs/independent-reproduction-protocol.md`, `docs/preservation-deposit-plan.md` | Agent protocol ready; no second-person review, deposit, DOI or release approval is claimed |
| `PUB-AGENT-PANEL-HF-20260802` | Review responsibility and optional public evidence mirror are bounded for a single-developer repository | `docs/single-developer-agent-panel-review-policy.md`, `docs/remaining-gates-autonomous-plan-20260802.json` | Agent-panel review policy active; Hugging Face is optional and not preservation, participant or authority evidence |
| `PUB-HOSTED-CLEAN-ROOM-20260802` | Dependency-isolated verifier runs on an exact revision in a hosted runner | `docs/hosted-evidence-batch-20260802.json`, [GitHub Actions run 30744486356](https://github.com/edithatogo/riopa-infrastructure/actions/runs/30744486356) | Passed for owner-authorized agent rehearsal; elapsed and release-authority evidence remain pending |
| `PUB-HOSTED-AGENT-CLEAN-ROOM-20260821` | Owner-authorized agent clean-room reproduction executes on the protected main revision | [GitHub Actions run 32422142075](https://github.com/edithatogo/riopa/riopa-infrastructure/actions/runs/32422142075), artifact `evidence-campaign-agent-workflows-20260821-agent-clean-room-32422142075` | Passed at `054f99d`; agent report is bounded evidence, not elapsed soak or promotion authority |
| `PUB-HOSTED-AGENT-CLEAN-ROOM-20260825` | Owner-authorized agent clean-room reproduction executes on the current protected main revision | [GitHub Actions run 32739052696](https://github.com/edithatogo/riopa/riopa-infrastructure/actions/runs/32739052696), `docs/evidence-campaign-status-20260821.json` | Passed at `2c93f9b`; agent evidence cannot substitute for exact-candidate isolated role-separated clean-room agent reproduction or publication authority |
| `PUB-AGENT-USER-WORKFLOWS-20260821` | Two distinct owner-authorized agent user journeys execute with content-bound logs | `scripts/run_agent_user_workflows.py`, `tests/test_hosted_evidence.py`, [GitHub Actions run 32423900230](https://github.com/edithatogo/riopa-infrastructure/actions/runs/32423900230), artifact `evidence-campaign-agent-workflows-20260821-agent-user-workflows-32423900230` | Passed at `8cf1ca6`; bounded agent evidence, not elapsed soak or promotion authority |
| `PUB-AGENT-USER-WORKFLOWS-20260825` | Two distinct owner-authorized agent user journeys execute on the current protected main | [GitHub Actions run 32739643452](https://github.com/edithatogo/riopa-infrastructure/actions/runs/32739643452), `docs/evidence-campaign-status-20260821.json` | Passed at `88f5376`; bounded agent evidence, not exact-candidate isolated role-separated clean-room agent reproduction or publication authority |
| `PUB-SINGLE-DEVELOPER-PANEL-V2-20260802` | Machine-readable gates, templates and live issue sources use agent-panel qualification semantics | `docs/single-developer-agent-panel-review-policy.md`, `docs/remaining-gates-campaign-v2-20260802.md`, `docs/panel-qualification-report-templates-20260801.json` | Review is agent-panel-owned; owner-authorized agent workflow evidence and authority decision remain distinct |
| `PUB-ALL-TRACK-PANEL-20260802` | Three isolated agent lenses and an orchestrator synthesis assess every Conductor track against one frozen revision and archive digest | `docs/panel-reports/20260802/manifest.json`, `scripts/validate_all_track_panel.py`, `tests/test_all_track_panel.py` | Reports complete for all 28 tracks; every final M6 disposition remains not-qualified; one stale facility-registry index finding was repaired after the frozen assessment |
| `PUB-CORRECTION-PACKAGE-20260803` | Immutable predecessor/successor correction package and downstream-notification fields are explicit | `docs/publication-correction-package-20260803.json`, `src/riopa_provenance/governance.py`, `src/riopa_provenance/publication.py`, `tests/test_governance.py`, `tests/test_publication.py` | Bounded WP-010 successor example is recorded; production downstream notification, isolated role-separated clean-room agent reproduction and release-authority acceptance remain open |
| `PUB-CORRECTION-PACKAGE-VALIDATION-20260822` | Correction package policy and predecessor/successor digest validation | `src/riopa_provenance/publication.py`, `tests/test_publication.py`, `docs/publication-correction-package-20260803.json` | Bounded package validates and rejects digest reuse; production notification and authority acceptance remain open |
| `PUB-PROTOCOL-CONTRACT-20260822` | Agent-panel conformance, clean-room and agent-user workflow protocols | `docs/single-developer-agent-panel-review-policy.md`, `docs/independent-reproduction-protocol.md`, `docs/release-gate-evidence-matrix.md`, `tests/test_hosted_evidence.py` | Protocol definition and bounded hosted lanes are present; claim classification, exact-candidate role-separated agent-panel evidence, publication and authority gates remain open |
| `PUB-CORRECTION-CONTRACT-CLOSEOUT-20260825` | Repository-owned correction/supersession package validation with digest-reuse rejection | `src/riopa_provenance/publication.py`, `tests/test_publication.py`, `docs/publication-correction-package-20260803.json` | Bounded validation passes; production downstream notification, isolated role-separated clean-room agent reproduction and release-authority acceptance remain open |
| `PUB-CLAIM-CLASSIFICATION-CONTRACT-20260825` | Claim-to-evidence traceability and exploratory/confirmatory/reference/prohibited classification rules | `docs/publication-claim-classification-contract-20260825.json`, `tests/test_publication_claim_classification.py` | Fail-closed classification contract passes; publication, participant, authority and elapsed gates remain open |
| `PUB-VALIDATOR-SELECTION-CONTRACT-20260825` | Agent-panel lenses, execution environments and analyst-independence criteria | `docs/publication-validator-selection-contract-20260825.json`, `tests/test_publication_validator_selection.py` | Selection contract passes; factual participant, preservation, publication and authority gates remain open |
| `PUB-VALIDATION-PACKET-20260825` | DOI-ready metadata, citation, provenance, SBOM, attestation and preservation sequence | `docs/publication-validation-packet-20260825.json`, `tests/test_publication_validation_packet.py` | Preparation packet is not a DOI or preservation receipt; protected attestations, accepted deposit, participant, elapsed and authority gates remain open |
| `PUB-VALIDATION-PACKET-INTEGRITY-20260829` | Machine-check the unpublished validation packet and referenced local contracts | `scripts/validate_publication_validation_packet.py`, `docs/publication-validation-packet-integrity-20260829.json`, `tests/test_publication_validation_packet_validator.py` | Historical packet integrity record remains immutable; DOI, publication, preservation, participant, elapsed and authority gates remain open |
| `PUB-VALIDATION-PACKET-SCOPE-20260829` | Successor scope control for the unpublished validation packet | `scripts/validate_publication_validation_packet.py`, `docs/publication-validation-packet-scope-20260829.json`, `tests/test_publication_validation_packet_validator.py` | Exact bounded regional public-datasets-only non-operational preview scope is enforced; DOI, publication, preservation, participant, elapsed and authority gates remain open |
| `PUB-CITATION-FIELDS-VALIDATION-20260830` | Machine-check all required citation fields in the DOI-ready preparation packet | `scripts/validate_publication_validation_packet.py`, `tests/test_publication_validation_packet_validator.py`, `docs/publication-citation-fields-validation-20260830.json` | Missing and malformed citation fields fail closed locally; DOI, publication, preservation, participant, elapsed and authority gates remain open |
| `PUB-VERSION-COORDINATION-20260825` | Software, schema, ontology, bounded data, model applicability and research-object versions are coordinated explicitly | `docs/publication-version-coordination-20260825.json`, `tests/test_publication_version_coordination.py` | Candidate manifest validates; release revision, protected attestations, preservation, participant, elapsed and authority gates remain open |
| `PUB-WORKFLOW-VERIFICATION-20260825` | Discovery, install, query, reproduce and cite paths are verified against repository-owned synthetic fixtures | `docs/publication-workflow-verification-20260825.json`, `tests/test_publication_workflow_verification.py` | Bounded local verification passes; isolated role-separated clean-room agent reproduction, publication, preservation, elapsed and authority gates remain open |
| `PUB-CITATION-GUIDANCE-20260825` | Versioned preview citation guidance and validation-evidence references | `docs/publication-citation-guidance-20260825.json`, `tests/test_publication_citation_guidance.py` | Preview guidance passes; stable publication identifier, preservation, isolated role-separated clean-room agent reproduction, elapsed and authority gates remain open |
| `PUB-CITATION-REVISION-VALIDATION-20260829` | Citation readiness requires a lowercase exact revision for bounded candidate references | `scripts/validate_publication_citation_readiness.py`, `docs/publication-citation-revision-validation-20260829.json`, `tests/test_publication_citation_readiness.py` | Negative revision test passes; publication, preservation, elapsed, participant and authority gates remain open |
| `PUB-RECEIPT-BATCH-CARDINALITY-20260829` | Reconciliation rejects duplicate target IDs within one receipt batch while retaining separate replay idempotence | `src/riopa_provenance/publication.py`, `tests/test_publication.py`, `docs/publication-receipt-batch-cardinality-20260829.json` | Duplicate-target negative test passes; remote acceptance, preservation, external, elapsed and authority gates remain open |
| `PUB-PACKAGE-PREPARATION-20260825` | Candidate infrastructure, methods, data-descriptor and applied publication package matrix | `docs/publication-package-preparation-20260825.json`, `tests/test_publication_package_preparation.py` | Package references and required checks are explicit; no deposit, DOI, isolated role-separated clean-room agent reproduction, elapsed qualification or authority decision is claimed |
| `PUB-REAL-DATA-CANDIDATE-20260825` | Owner-authorized agent reproduces one bounded real-data archive release with exact artifact hashes | `docs/publication-real-data-release-candidate-20260825.json`, `evidence/wp007-real-slice/manifest.json`, `tests/test_publication_real_data_candidate.py`, `bash scripts/ci_reproducibility.sh` | Digest-bound candidate passes; isolated role-separated clean-room agent reproduction, attestation, preservation, elapsed qualification and authority remain open |
| `PUB-APPLIED-BENCHMARK-20260825` | Owner-authorized agent reproduces one manifest-bound applied benchmark with explicit national projection boundary | `docs/publication-applied-benchmark-reproduction-20260825.json`, `examples/wp010-performance-benchmark/`, `tests/test_publication_applied_benchmark_reproduction.py`, `tests/test_wp010_performance_contract.py`, `tests/test_resilience_matrix.py` | Regional synthetic run passes; national-scale measurement, resource/cost instrumentation, isolated role-separated clean-room agent reproduction, preservation, elapsed qualification and authority remain open |
| `PUB-DEVIATIONS-LIMITATIONS-20260825` | Findings from repository-owned real-data and applied-benchmark reproductions are resolved and published without erasing open gates | `docs/publication-deviations-limitations-20260825.json`, `tests/test_publication_deviations_limitations.py` | Findings pass with limitations; external participation, preservation, elapsed evidence, national-scale measurement and release authority remain open |

## Exact-plan-bound recovery (2026-08-31)

`build_publication_resume_plan` binds a restored journal to the intended ready
plan before deterministic receipt reconciliation. Missing receipts require
provider reconciliation, not a new deposit. The bounded contract and negative
tests are recorded in `docs/publication-plan-bound-resume-20260831.md` and
`tests/test_publication.py` (issue #129, WP-003, plan R4). No authenticated
provider acceptance, publication, preservation or maturity promotion is claimed.

## Local recovery command (2026-08-31)

The local-only `riopa publication resume` operator entry point is documented in
`docs/publication-resume-cli-20260831.md` and exercised by
`tests/test_publication_resume_cli.py` (WP-003, issue #129, plan R5). It rejects
ambiguous recovery JSON and emits a key-sorted exact-plan projection without
modifying inputs or contacting providers. This is local recovery tooling, not
authenticated provider reconciliation or evidence that remote publication
completed.

## Blocking defects

- The repository-owned claim-classification and publication-package contracts
  are implemented and validated; they do not constitute publication or release
  acceptance.
- Exact stable-candidate isolated role-separated clean-room agent reproduction,
  publication/deposition and restore acceptance, correction notification,
  elapsed beta/RC evidence and accountable release-authority acceptance remain
  open.

## Repository-owned closeout slice (2026-08-24)

The publication state machine, correction-package validator, clean-room and
agent-user workflow protocols, and bounded hosted reports are linked above and
validated by `bash scripts/ci_quality.sh` at protected `main` revision
`a2f8f93bacc54ddf66203766c15a1c9f2506beb8`. These contracts establish
reproducibility boundaries; they do not establish publication, independent
participant evidence or promotion authority.

## Decisions, exceptions and limitations

- This is a single-developer repository. Role-separated subagent panels and
  owner-authorized agent workflows provide clean-room and user/operator journey
  evidence but cannot substitute for provider, elapsed-operation or accountable
  release-authority facts.
- Public-source, bounded non-operational technical-preview scope remains in
  force; unsupported national, network, timetable, facility, clinical and
  dispatch claims remain disabled.
- A fixture, hosted rehearsal, Hugging Face mirror or candidate DOI-ready
  packet is not a publication or preservation acceptance receipt.

## Review and handover

Required agent-panel lenses: Governance analyst, Research-object analyst, Agent workflow analyst, Scientific-methods analyst.

This index is deliberately non-assertive while the track remains `active` at
M1. Status may advance only through `conductor/workflow.md`; evidence must be
immutable or version-addressed, agent-panel qualified where required, and
sufficient for the applicable release gates.
