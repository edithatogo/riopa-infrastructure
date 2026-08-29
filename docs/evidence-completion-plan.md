# Evidence completion plan

This plan separates repository-owned agent-panel evidence from facts that must
be supplied by a source custodian, hosted system, preservation provider or the
sole accountable release authority.

| Evidence lane | Repository preparation | Required closure evidence | Current state | Fallback |
|---|---|---|---|---|
| WP-010 reproduction | Frozen handoff, digest-bound validator, hosted clean-room run and two distinct owner-authorized agent journeys | Role-separated agent logs, exact revision/bundle digest, findings, dissent/disposition and content-bound synthesis for each promotion candidate | **Complete for the bounded work package**; issue #149 is superseded by the sole-developer policy | Re-run the agent panel when a promotion candidate changes; do not infer elapsed operation or external-system acceptance |
| Source authority | Metadata-only request packet, acquisition schema and fail-closed validator | Custodian, exact revision, rights, coverage, freshness, exclusions, withdrawal route and expiry | Deferred; no acquisition authorised | Regional-only scope |
| Ontology/conformance | Versioned fixture, migration tests, digest-bound manifest and structural validator | Persistent publication ID, licence, SHACL result and non-Python round-trip | Unpublished/bounded-pending | Python-only unpublished profile |
| Pilot governance | Decision record, rights inventory, source disposition and Zenodo record | Review/adjudication on or before 2026-08-31, earlier on material change | Approved bounded pilot | Preserve current packet; issue successor on change |
| Restore/rollback | Deterministic local snapshot/restore/rollback harness and tamper tests (`docs/restore-rollback-evidence-20260801.md`) | Production/DR drill logs, timestamps, recovery-point/object hashes, owner acknowledgement and correction/withdrawal exercise | Local evidence implemented; operational qualification remains open | Keep promotion blocked and remediate runbooks after any failed drill |
| Performance/capacity | Reproducible synthetic regional contract/runner under `examples/wp010-performance-benchmark/` | Representative beta/RC workload, latency/throughput/resource/storage/cost measurements and national-scale validation | Regional synthetic measurement available; national result is projection only | Publish measured envelope and defer scale claims |
| Panel qualification | Generated pending templates and validated manifest for all 28 tracks (`docs/panel-qualification-report-templates-20260801.json`) | Completed three-agent reports with evidence links, concordance/dissent and disposition per track | Infrastructure complete; all track dispositions remain pending | Retain open status and technical-preview scope |
| Release authority | Beta/RC/stable checklists and preserved artifacts | Named authority, operational evidence, soak, reproductions and signed approval | Open for all promotion tiers | Remain at technical preview |
| Hosted quality gates | CI workflows, PR quality checklist and fail-closed blocker register (`docs/hosted-quality-gate-blockers-20260801.md`) | GitHub ruleset, Renovate, Codecov/OIDC and exact-head check receipts | Repository preparation complete; hosted settings remain unverified | Keep hosted rows open and do not infer protection or coverage from local results |

## Operating sequence

1. Re-run the role-separated agent panel for any changed promotion candidate.
2. Complete the bounded-pilot review by 2026-08-31 or sooner on trigger.
3. Publish and qualify the ontology if formal authority is required.
4. Seek national source authority only if scope expansion is approved.
5. Advance beta, RC and stable gates independently; do not infer one from another.

No lane may be marked complete from local tests alone when its required
evidence is external or authority-bound.
