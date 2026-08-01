# Evidence completion plan

This plan separates repository-owned preparation from evidence that must be
supplied by an external operator, source custodian or release authority.

| Evidence lane | Repository preparation | Required external evidence | Current state | Fallback |
|---|---|---|---|---|
| WP-010 reproduction | Frozen handoff, approval record, digest-bound validator and report template | Independent operator, clean-room logs, exact revision/bundle digest, findings, safety/rights adjudication and immutable report | Blocked; issue #149 remains open; internal panel remains rehearsal only | Technical-preview/pilot only |
| Source authority | Metadata-only request packet, acquisition schema and fail-closed validator | Custodian, exact revision, rights, coverage, freshness, exclusions, withdrawal route and expiry | Deferred; no acquisition authorised | Regional-only scope |
| Ontology/conformance | Versioned fixture, migration tests, digest-bound manifest and structural validator | Persistent publication ID, licence, SHACL result and non-Python round-trip | Unpublished/bounded-pending | Python-only unpublished profile |
| Pilot governance | Decision record, rights inventory, source disposition and Zenodo record | Review/adjudication on or before 2026-08-31, earlier on material change | Approved bounded pilot | Preserve current packet; issue successor on change |
| Restore/rollback | Deterministic local snapshot/restore/rollback harness and tamper tests (`docs/restore-rollback-evidence-20260801.md`) | Production/DR drill logs, timestamps, recovery-point/object hashes, owner acknowledgement and correction/withdrawal exercise | Local evidence implemented; operational qualification remains open | Keep promotion blocked and remediate runbooks after any failed drill |
| Performance/capacity | Reproducible synthetic regional contract/runner under `examples/wp010-performance-benchmark/` | Representative beta/RC workload, latency/throughput/resource/storage/cost measurements and national-scale validation | Regional synthetic measurement available; national result is projection only | Publish measured envelope and defer scale claims |
| Panel qualification | Generated pending templates and validated manifest for all 28 tracks (`docs/panel-qualification-report-templates-20260801.json`) | Completed three-agent reports with evidence links, concordance/dissent and disposition per track | Infrastructure complete; all track dispositions remain pending | Retain open status and technical-preview scope |
| Release authority | Beta/RC/stable checklists and preserved artifacts | Named authority, operational evidence, soak, reproductions and signed approval | Open for all promotion tiers | Remain at technical preview |

## Operating sequence

1. Obtain the external reproduction report.
2. Complete the bounded-pilot review by 2026-08-31 or sooner on trigger.
3. Publish and qualify the ontology if formal authority is required.
4. Seek national source authority only if scope expansion is approved.
5. Advance beta, RC and stable gates independently; do not infer one from another.

No lane may be marked complete from local tests alone when its required
evidence is external or authority-bound.
