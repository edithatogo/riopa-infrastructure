# Remaining-gates campaign v2

## Recommendation

Continue with GitHub Actions as the primary evidence runner, run the beta
observation lane daily, reconcile live GitHub issue bodies from validated
Conductor sources, and use orchestrated agent panels for every repository
qualification. Keep Hugging Face as a budget-capped second failure domain; do
not use community Hub datasets as national or source-authority evidence.

## Current evidence

- The exact `f8135fc` CI and CodeQL runs passed.
- Five GitHub-hosted technical-preview lanes passed: recovery/rollback,
  agent clean-room, scale smoke, operational observation and RC observation.
- The GitHub connector found 28 open track parents, still represented as M1.
  Some live issue bodies retained the old reviewer wording even though local
  Conductor sources had moved to agent-panel roles.
- Hugging Face is authenticated as `edithatogo`; no Jobs exist. Searches for
  `LINZ`, `New Zealand` and `OpenStreetMap New Zealand` found no credible
  authoritative national geospatial workload.

## Gate plan

| Gate | Implement now | Completion evidence | Contingency |
|---|---|---|---|
| Review and qualification | Replace remaining independent/scientific/human-review requirements with two or more agent analysts and an orchestrator synthesis; synchronise GitHub issue bodies | Content-bound panel reports and resolved findings for every track | Preserve dissent and keep the affected track open |
| Operational beta | Run the bounded observation workflow daily from 2026-08-02; roll every hashed receipt into the latest cumulative campaign artifact | At least 90 elapsed days, no observation gap over 36 hours, three explicitly labelled operational cycles and failure/backfill/recovery evidence | Change the qualification epoch, and therefore reset the clock, after a material candidate or instrumentation change; ordinary beta commits do not reset it |
| Release-candidate soak | Start only after the exact RC is frozen | At least 30 days of exact-candidate SLO, defect, recovery and capacity evidence | Defer RC; earlier observations remain rehearsal evidence |
| Hosted recovery | Retain the passed GitHub technical drill and stage a revision/image-pinned Hugging Face fallback | Production-representative full restore with RPO/RTO, fixity and failure-domain evidence | Keep production DR open; optionally run the budget-capped HF drill after cost approval |
| National scale | Freeze an authoritative public workload manifest and measurement contract | Measured national ingestion/query/accessibility/optimisation envelopes and costs | Run national-volume synthetic scale tests but prohibit nationally representative claims |
| Agent-operated workflows | Use owner-authorized agents for execution and panel assessment | One agent operator and two distinct agent-user workflow records if beta/RC/stable criteria remain unchanged | Remain technical preview or formally change the release scope |
| Release authority | Assemble a digest-bound decision packet for the single accountable owner | Signed promotion, deferral or rejection record with scope, expiry and rollback conditions | No beta/RC/stable promotion |
| Cross-track completion | Reconcile each GitHub issue to content-bound evidence in dependency order | No open v1 blocker, expired waiver or missing panel disposition | Explicitly defer scope without raising maturity |

## Platform options

1. **GitHub Actions primary — recommended.** It is already exact-head,
   immutable-action-pinned and proven by the five hosted observations. The
   daily lane now restores the preceding artifact, validates and hashes every
   receipt, rebuilds the fail-closed ledger, and uploads the cumulative history.
   This rolling copy prevents an early receipt disappearing solely because its
   original 90-day artifact expires; a missed/failed aggregation remains a
   visible break and does not silently pass the gate.
2. **Hugging Face Jobs secondary.** Use `cpu-basic` with a 30-minute ceiling
   only after the image digest and bootstrap pass locally. At the observed
   rate, the cost ceiling is less than USD 0.01, but submission still creates
   billable external state.
3. **Local-only fallback.** Continue deterministic rehearsals without making
   hosted, production, national or elapsed-time claims.

## Library decision

Retain DuckDB, PyArrow, PyProj, Shapely, HTTPX and JSON Schema. For the first
real capacity campaign, consider an optional benchmark-only extra containing
`pyperf` for noise-aware timing and `psutil` for process memory/CPU metrics.
Do not add them until the measurement harness consumes them. Avoid adding
Hugging Face `datasets`, GeoPandas, Locust, ASV, Pandera or Frictionless now:
none closes a remaining gate and each expands dependency and audit surface.

The staged Hugging Face runner decision is machine-readable in
`docs/hugging-face-evidence-runner-plan-20260802.json`.
