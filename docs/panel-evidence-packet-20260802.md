# Bounded preview panel evidence packet

Status: `template-ready`; no track is qualified by this packet.

This packet is the execution handoff for the five-track bounded public-data
preview batch. The machine-readable batch manifest is
[`panel-qualification-batch-20260802.json`](panel-qualification-batch-20260802.json).

## Execution contract

Before a report is accepted, the orchestrator must freeze one source revision
and one operator-bundle SHA-256, then give those exact values to all three
roles:

- `reproducer`
- `adversarial-reviewer`
- `evidence-auditor`

Each role writes one JSON report satisfying the validator contract. Reports
must include a stable identifier, track and bounded scope, UTC evaluation time,
findings, evidence references, exact source revision, bundle digest,
disposition and dissent. Run:

```sh
uv run python scripts/validate_panel_reports.py \
  reports/panel/<batch>/<track>/reproducer.json \
  reports/panel/<batch>/<track>/adversarial-reviewer.json \
  reports/panel/<batch>/<track>/evidence-auditor.json
```

The validator establishes concordance only. It does not establish independent
external reproduction, user validation, operational soak, release authority or
release readiness.

## Fail-closed handling

- Missing, malformed or digest-mismatched reports remain pending.
- A `fail` disposition blocks panel concordance and opens remediation.
- Dissent is retained, including an empty list when there is no dissent.
- Subagent reports cannot be represented as external person/operator evidence.
- No report, digest or disposition may be inferred from an empty template slot.

After execution, link only immutable report locations and SHA-256 values from
the report manifests. Until then, this packet remains preparation evidence for
the technical-preview campaign.
