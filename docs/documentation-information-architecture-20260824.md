# Documentation information architecture

This is the repository-owned information architecture for the single-developer
RIOPA Infrastructure repository. Agents may execute and assess workflows, but
the accountable release authority remains the repository owner.

## Audiences and entry points

| Audience | Primary workflow | Entry point | Normative references |
|---|---|---|---|
| Researcher/analyst | Install, inspect a bounded public or synthetic package, reproduce a result | `README.md`, `docs/methods-output-contract.md` | `conductor/product.md`, schemas, methods contract |
| Connector operator | Validate a source request, capture, quarantine and diagnose a failure | `docs/source-acquisition-runbook.md`, connector authoring guide | capture/retry/health modules, source schemas |
| Contributor | Run checks, add a focused change and update its Conductor evidence | `AGENTS.md`, `conductor/workflow.md` | project quality harness, selected track plan |
| Maintainer/release authority | Review evidence, sign or reject a promotion, and preserve rollback boundaries | `docs/conformance-and-release-verification.md`, `conductor/releases.json` | release gates, security and operations tracks |
| Agent-panel analyst | Assess a frozen packet and record limitations without creating participant evidence | `docs/single-developer-agent-panel-review-policy.md` | panel manifest, evidence schemas |

## Supported workflows

1. **Install and validate:** use Python 3.14, `uv sync --frozen`, then the
   repository quality harness.
2. **Offline connector rehearsal:** use bounded fixtures and the adapter
   authoring guide; live endpoints and rights decisions are separate gates.
3. **Research-object build:** build from a content-addressed manifest, verify
   closure and checksums, and preserve generated projections as projections.
4. **Reproduce a claim:** bind the exact revision, source/capture digest and
   workload manifest; report missing evidence as pending.
5. **Release review:** compare the tier-specific gate matrix, signed evidence,
   preservation receipts, soak status, rollback conditions and authority record.

## Interface map

- CLI and Python APIs: `src/riopa_provenance/cli.py` and the public package.
- Machine-readable contracts: `schemas/`, `examples/minimal/` and `conformance/`.
- Normative programme state: `conductor/`, `project/issues.yaml` and the
  generated roadmap validators.
- Operational procedures: `docs/runbooks/`, `docs/operations-and-support.md`
  and the operations track evidence index.

The documentation does not enable network, timetable, facility, national,
clinical or dispatch claims. Those remain disabled until separately evidenced.
