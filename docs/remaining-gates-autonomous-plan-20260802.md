# Remaining-gates autonomous execution plan

The recommended route is a fail-closed, single-developer campaign: restore the
exact-head CI baseline, use panels of agents for every review, freeze hosted
execution inputs, and collect actual hosted, elapsed, scale, participant and
authority evidence without relabelling rehearsals as outcomes.

The live GitHub snapshot contained 146 open issues, including 28 track parents.
CodeQL passed at the observed head, while CI failed on formatting; the formatting
defect is repository-owned and is fixed in this change. GitHub-hosted run
`30744372005` subsequently passed the recovery/rollback technical-preview lane
at exact revision `347cf53`; its content-bound receipt is recorded in
`docs/hosted-recovery-execution-20260802.json`. Production disaster-recovery
qualification remains open. The machine-readable
snapshot and gate options are in
`docs/remaining-gates-autonomous-plan-20260802.json`.

## Options and recommendation

1. **GitHub Actions first — recommended.** Extend the existing pinned-action
   workflows for recovery, scheduled observations and bounded performance. It
   has the lowest trust and maintenance delta and keeps evidence beside the
   exact commit.
2. **Hugging Face Jobs as a secondary hosted runner.** A read-only assessment
   confirmed authenticated CLI access and `cpu-basic` capacity at an observed
   USD 0.01/hour. Use it only for a budget-capped, revision-pinned job when the
   GitHub runner cannot model the exercise. Submission is deliberately not part
   of this change because it creates billable external state.
3. **Local-only campaign.** Continue deterministic rehearsals, but retain all
   hosted, elapsed and external claims as blocked. This is the no-cost fallback,
   not a route to stable qualification.

Hugging Face is useful as an optional revision-addressed mirror for a public
workload packet and as a secondary compute failure domain. It is not the source
authority, preservation DOI, external participant or release authority. The
search for `New Zealand geospatial` returned no matching Hub dataset, so the
campaign must not silently substitute a community dataset for its governed
public-source manifest.

## Execution sequence

1. Keep CI and CodeQL green on the exact candidate head.
2. Freeze the candidate, SLOs, public workload manifest and recovery bundle.
3. Run an orchestrated multi-agent qualification panel and resolve its findings.
4. Execute hosted recovery and bounded performance, recording runner identity,
   timestamps, resource tier, commands, logs, output hashes and costs.
5. Start digest-chained operational-cycle and RC-soak clocks; reset the affected
   clock after material changes.
6. Collect actual external operator/user workflow evidence if those promotion
   criteria remain in scope.
7. Assemble the digest-bound decision packet for accountable promotion.
8. Reconcile each open issue and track to implementation and evidence; archive
   only through the Conductor workflow.

## Libraries

Retain DuckDB, PyArrow, PyProj, Shapely, HTTPX and JSON Schema. They already
cover analytical execution, geospatial correctness, transport and contracts.
`huggingface_hub`/`fsspec` would help only when in-process `hf://` access is
required; Pandera or Frictionless would add a second validation layer. None
closes a present gate, so adding them now would create more dependency and SBOM
work. The installed `hf` CLI is sufficient for staged Hub and Jobs operations.

## Contingencies

- If GitHub-hosted recovery cannot model the required failure domain, prepare a
  budget-capped Hugging Face `cpu-basic` job and obtain explicit cost approval
  before submission.
- If no authoritative national public workload is available, publish bounded
  regional/synthetic measurements and keep national claims disabled.
- If external participant evidence is absent, release only as a technical
  preview even after agent-panel qualification.
- If the accountable decision is absent or declines promotion, preserve the
  packet and keep beta/RC/stable gates open.
