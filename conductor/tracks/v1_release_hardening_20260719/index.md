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

## Blocking defects

- Stable-v1 completion remains blocked by the gates listed in the readiness baseline, including external reproduction, user validation, operational soak, preserved signed release and release-authority decision.

## Campaign gate capability map

| Gate | Repository-owned work | Required external or elapsed evidence |
|---|---|---|
| Hosted recovery execution | Prepare manifests, scripts and verification; execute only where an authenticated hosted environment exists | Hosted/DR run logs, timestamps, recovery-point hashes and independent verification |
| Operational cycles and RC soak | Start logging, automate observations and maintain digests | Actual elapsed cycles and soak duration; interruptions reset the clock |
| National-scale workload measurements | Design workloads and run bounded public-data/regional benchmarks | Approved national workload, infrastructure and measured results |
| External operator/user workflows | Prepare frozen bundles, instructions and report templates; run panel rehearsals | External operator reproduction and two distinct external-user reports |
| Accountable release-authority decision | Assemble the digest-bound decision packet and draft options | Named authority's signed tier decision with expiry and rollback conditions |

Agent panels can prepare and qualify repository-owned evidence, but cannot
substitute for external participants, elapsed qualification time or accountable
release authority.

## Decisions, exceptions and limitations

- None recorded.

## Review and handover

Required agent-panel lenses: Governance analyst, API/schema analyst, Provenance analyst, Security analyst, Data-governance analyst, Operations analyst, Performance analyst, Interoperability analyst, Research-object analyst, External-user workflow analyst, Quantitative methods analyst, Scientific-methods analyst.

This index records a bounded repository-owned readiness baseline while the track remains `active`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, independently reviewed where required, and sufficient for the applicable release gates.

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
