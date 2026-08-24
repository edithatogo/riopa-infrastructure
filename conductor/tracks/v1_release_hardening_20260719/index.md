# Evidence index: Stable v1 release hardening and general availability

- **Track ID:** `v1_release_hardening_20260719`
- **Status:** `active`
- **Target release:** `1.0.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Governance`
- **Risk / priority:** `Critical` / `P0`
- **V1 critical:** `yes`
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Release authority
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/139

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| V1-BASELINE-20260801 | Fail-closed stable-v1 readiness baseline | `docs/v1-release-readiness-baseline-20260801.json`, `tests/test_v1_release_readiness.py` | Repository checks passing; promotion explicitly blocked |
| V1-REMAINING-GATES-20260802 | Single-developer gate plan, platform observations, hosted receipt runner, library decision and contingencies | `docs/remaining-gates-autonomous-plan-20260802.json`, `docs/remaining-gates-autonomous-plan-20260802.md`, `docs/single-developer-agent-panel-review-policy.md`, `.github/workflows/evidence-campaign.yml`, `scripts/record_hosted_evidence.py`, `schemas/hosted-evidence.schema.json`, `tests/test_remaining_gates_plan.py`, `tests/test_hosted_evidence.py` | Agent-panel policy and hosted technical-preview runner implemented; actual elapsed, national, participant and authority evidence remains open |
| V1-HOSTED-RECOVERY-20260802 | Exact-revision recovery/rollback technical-preview drill executes in GitHub's hosted environment | `docs/hosted-recovery-execution-20260802.json`, [GitHub Actions run 30744372005](https://github.com/edithatogo/riopa-infrastructure/actions/runs/30744372005) | Passed at `347cf53`; production DR, participant, elapsed-soak and authority gates remain open |
| V1-HOSTED-AGENT-RECOVERY-20260821 | Owner-authorized agent recovery/rollback rehearsal executes on protected main | [GitHub Actions run 32422145056](https://github.com/edithatogo/riopa/riopa-infrastructure/actions/runs/32422145056), artifact `evidence-campaign-agent-workflows-20260821-recovery-rollback-32422145056` | Passed at `054f99d`; production DR, elapsed-soak and owner tier decision remain open |
| V1-HOSTED-AGENT-RECOVERY-20260825 | Owner-authorized agent recovery/rollback rehearsal executes on the current protected main | [GitHub Actions run 32739052364](https://github.com/edithatogo/riopa/riopa-infrastructure/actions/runs/32739052364), `docs/evidence-campaign-status-20260821.json` | Passed at `2c93f9b`; production DR, external evidence, elapsed-soak and accountable tier decision remain open |
| V1-HOSTED-BATCH-20260802 | Exact-revision agent clean-room, scale-smoke, operational and RC-soak observations execute in hosted runners | `docs/hosted-evidence-batch-20260802.json` | Four lanes passed at `6fcbe29`; national scale, elapsed duration, additional agent workflows, track qualification and authority remain open |
| V1-CAMPAIGN-V2-20260802 | Live GitHub/Conductor drift, daily evidence schedule, revision-bound ledger, Hugging Face fallback and library choices are reconciled | `docs/remaining-gates-campaign-v2-20260802.md`, `docs/hugging-face-evidence-runner-plan-20260802.json`, `.github/workflows/evidence-campaign.yml`, `scripts/build_campaign_ledger.py`, `tests/test_campaign_ledger.py` | Repository review uses agent panels; live issue sync and elapsed/external/authority evidence remain separately tracked |
| V1-GITHUB-ISSUE-SYNC-20260802 | Validated Conductor projections are reconciled to live GitHub issues after the agent-panel migration | `docs/github-issue-sync-20260802.json`, `project/issues.yaml` | 151 generated records applied without error; 140 updated and 11 missing phase issues created; open work remains open |
| V1-GITHUB-MAIN-PROTECTION-20260802 | The single-developer main branch enforces exact hosted checks without a human-review requirement | `docs/github-main-protection-20260802.json` | Strict CI and CodeQL checks, linear history, conversation resolution and admin enforcement enabled; force-push and deletion disabled |
| V1-ALL-TRACK-PANEL-20260802 | Three content-bound agent lenses and an orchestrator synthesis cover all 28 tracks | `docs/panel-reports/20260802/manifest.json`, `docs/panel-reports/20260802/orchestrator-synthesis.json` | Report-availability gate closed; all 28 M6 dispositions remain not-qualified and factual release gates remain open |
| V1-CAMPAIGN-V3-20260802 | Current protected-head GitHub state, Hugging Face execution outcome, remaining gate sequence, library options and contingencies are reconciled | `docs/remaining-gates-campaign-v3-20260802.json`, `docs/remaining-gates-campaign-v3-20260802.md`, `tests/test_campaign_v3.py` | Exact-head CI and CodeQL pass; no open PRs; 14 evidenced phase issues closed and 141 issues remain; Hugging Face job was not created after an HTTP 402 response; gates remain fail-closed |
| V1-PYTHON314-QUALITY-20260803 | Current Python 3.14 mainline reaches the 90% branch-aware coverage gate | `docs/python314-quality-evidence-20260803.json` | 623 tests passed at 91.96%; external, elapsed and authority gates remain open |
| V1-FEATURE-FREEZE-20260803 | Bounded normative-surface inventory and explicit freeze exclusions | `docs/v1-feature-freeze-inventory-20260803.json` | Python 3.14/runtime, schema, CLI and publication surfaces are inventoried; full compatibility diff remains open |
| V1-RC-HANDOVER-20260803 | Digest-bound candidate handover packet links current readiness evidence and fail-closed promotion decision | `docs/v1-rc-validation-handover-20260803.json` | Handover packet prepared; external, elapsed, national-scale, signed-preservation and accountable-authority gates remain open |
| V1-RC-CANDIDATE-20260825 | Exact protected-main RC candidate observation with candidate revision binding | [GitHub Actions run 32740183479](https://github.com/edithatogo/riopa/riopa-infrastructure/actions/runs/32740183479), `docs/evidence-campaign-status-20260821.json` | Candidate drill passed at `159b8d7`; 30-day exact-RC soak, external workflows, signed preservation and accountable decision remain open |
| V1-RC-CANDIDATE-REPLAY-20260825 | Exact protected-main RC candidate replay after checkout-binding and campaign-isolation fixes | [GitHub Actions run 32741649873](https://github.com/edithatogo/riopa/riopa-infrastructure/actions/runs/32741649873), `docs/evidence-campaign-status-20260821.json` | Candidate `b572d7a` passed and starts a fresh 30-day segment; external workflows, signed preservation and accountable decision remain open |
| V1-RC-CANDIDATE-STATUS-VALIDATED-20260825 | Exact protected-main RC observation on the candidate containing campaign-status validation | [GitHub Actions run 32743048406](https://github.com/edithatogo/riopa/riopa-infrastructure/actions/runs/32743048406), `docs/evidence-campaign-status-20260821.json` | Candidate `bc571ca` passed and starts a fresh 30-day segment; external workflows, signed preservation and accountable decision remain open |
| V1-PARENT-MATURITY-20260803 | Consolidated inventory of all parent Conductor tracks below their M6 target | `docs/parent-track-maturity-report-20260803.json`, `scripts/report_parent_maturity.py` | 28/28 tracks remain below M6; inventory is fail-closed and does not substitute for track evidence |
| V1-FINAL-GATES-20260803 | Final elapsed-soak, agent-workflow, authority and stable-approval gates are consolidated in one fail-closed status record | `docs/final-release-gates-status-20260803.json` | Beta/RC duration, agent workflows, owner decision and stable approval remain pending |
| V1-SCOPE-POLICY-20260804 | Owner-authorized scope, participant, elapsed-time and authority policy | `docs/release-scope-and-evidence-policy-20260804.json` | Preparation authorized; promotion remains forbidden until qualifying evidence and a named signed authority decision exist |
| V1-BETA-ACCELERATION-20260804 | GitHub Actions runs qualifying daily observations alongside a separated retrospective replay lane | `docs/beta-campaign-acceleration-plan-20260804.json`, `.github/workflows/evidence-campaign.yml` | Supplemental replay can accelerate technical learning but contributes zero elapsed-time qualification |
| V1-FEATURE-FREEZE-VALIDATION-20260822 | Executable validation of the bounded feature-freeze inventory and explicit open findings | `scripts/validate_v1_feature_inventory.py`, `tests/test_v1_release_readiness.py`, `docs/v1-feature-freeze-inventory-20260803.json` | Repository inventory validates; full compatibility diff and external/release gates remain open |
| V1-NORMATIVE-SURFACE-INVENTORY-20260825 | Repository-wide inventory of public API modules, schemas, ontology bindings, CLI groups and supported file formats | `docs/v1-normative-surface-inventory-20260825.json`, `tests/test_v1_release_readiness.py` | Inventory is complete and path-validated; compatibility diff, external reproduction, elapsed soak and release-authority gates remain open |

## Blocking defects

- Stable-v1 completion remains blocked by the gates listed in the readiness baseline, including external reproduction, user validation, operational soak, preserved signed release and release-authority decision.

## Campaign gate capability map

| Gate | Repository-owned work | Required external or elapsed evidence |
|---|---|---|
| Hosted recovery execution | Prepare manifests, scripts and verification; execute only where an authenticated hosted environment exists | Hosted/DR run logs, timestamps, recovery-point hashes and independent verification |
| Operational cycles and RC soak | Start logging, automate observations and maintain digests | Actual elapsed cycles and soak duration; interruptions reset the clock |
| National-scale workload measurements | Design workloads and run bounded public-data/regional benchmarks | Approved national workload, infrastructure and measured results |
| Agent-operated operator/user workflows | Prepare frozen bundles, instructions and report templates; execute owner-authorized agent workflows and panel rehearsals | Two distinct agent-executed workflow reports with exact revision and limitations |
| Quality frontier qualification | Python 3.14 suite, branch-aware coverage, applicability and explicit exclusions recorded | `docs/quality-frontier-qualification-20260803.json`, `.github/workflows/mutation.yml`, `scripts/check_mutation_score.py`, `scripts/verify_conformance_parity.py`, `scripts/check_workflow_lint.py`, `scripts/check_tracked_secrets.py` | Bounded mutation lane measured 68.78% against a 65% floor; Python/Node corpus parity is now hosted and receipt-backed; Rust/SDK/external-client parity and provider-side scanning remain open |
| Solo-maintainer security context | Canonical agent, contribution, security and protected-main boundaries with a one-command drift check | `docs/solo-maintainer-security-context.md`, `scripts/validate_repo_context.py`, `tests/test_repo_context.py`, `docs/renovate-codecov-rollout-20260803.json` | Repository-owned context and live protection verifier are present; Renovate, Codecov/OIDC and provider-side scanning remain external gates |
| Quality frontier closeout | Issue #147 subissues closed with explicit bounded qualifications and non-substitutable release boundaries | `docs/quality-frontier-closeout-20260821.json`, `tests/test_quality_frontier_closeout.py` | Repository-owned hardening scope qualified; broader parity, provider services, elapsed, participant and authority gates remain open |
| Owner accountable release-authority decision | Assemble the digest-bound decision packet and draft options | Repository owner's signed tier decision with expiry and rollback conditions |
| Single-person authority context | Record owner accountability and agent-operated workflow roles without authorising promotion | `docs/single-person-operating-model-20260821.md`, `docs/owner-accountable-authority-20260821.json` | Owner accountability confirmed; tier-specific promotion decision remains unrecorded |
| Evidence campaign status snapshot | Consolidate successful hosted lanes and the active beta epoch in one dated, fail-closed status record | `docs/evidence-campaign-status-20260821.json` | Hosted evidence is accumulating; 90-day/three-cycle duration and owner promotion decision remain pending |

Agent panels can prepare and qualify repository-owned evidence, but cannot
substitute for elapsed qualification time or the repository owner's accountable
release decision.

## Decisions, exceptions and limitations

- None recorded.

## Review and handover

Required agent-panel lenses: Governance analyst, API/schema analyst, Provenance analyst, Security analyst, Data-governance analyst, Operations analyst, Performance analyst, Interoperability analyst, Research-object analyst, Agent workflow analyst, Quantitative methods analyst, Scientific-methods analyst.

This index records a bounded repository-owned readiness baseline while the track remains `active`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, agent-panel qualified where required, and sufficient for the applicable release gates.

## Review record

- Review scope: v1 readiness baseline, plan status, metadata and registry through
  `1bac0cc`.
- Finding: the baseline was incorrectly used as evidence that the complete
  normative API/schema/ontology inventory was finished.
- Fix: restored task 1.1 to pending and recorded the boundary explicitly.
- Follow-up: mapped each remaining campaign gate to repository-owned preparation
  and its non-substitutable external/elapsed evidence requirement.
- Follow-up: adopted the single-developer agent-panel policy, recorded the live
  GitHub/Hugging Face assessment, library decision, options and contingencies.
