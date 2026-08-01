# Evidence completion plan

This plan separates repository-owned preparation from evidence that must be
supplied by an external operator, source custodian or release authority.

| Evidence lane | Repository preparation | Required external evidence | Current state | Fallback |
|---|---|---|---|---|
| WP-010 reproduction | Frozen handoff, approval record, digest-bound validator and report template | Independent operator, clean-room logs, exact revision/bundle digest, findings, safety/rights adjudication and immutable report | Blocked; issue #149 remains open | Technical-preview/pilot only |
| Source authority | Metadata-only request packet, acquisition schema and fail-closed validator | Custodian, exact revision, rights, coverage, freshness, exclusions, withdrawal route and expiry | Deferred; no acquisition authorised | Regional-only scope |
| Ontology/conformance | Versioned fixture, migration tests, digest-bound manifest and structural validator | Persistent publication ID, licence, SHACL result and non-Python round-trip | Unpublished/bounded-pending | Python-only unpublished profile |
| Pilot governance | Decision record, rights inventory, source disposition and Zenodo record | Review/adjudication on or before 2026-08-31, earlier on material change | Approved bounded pilot | Preserve current packet; issue successor on change |
| Release authority | Beta/RC/stable checklists and preserved artifacts | Named authority, operational evidence, soak, reproductions and signed approval | Open for all promotion tiers | Remain at technical preview |

## Operating sequence

1. Obtain the external reproduction report.
2. Complete the bounded-pilot review by 2026-08-31 or sooner on trigger.
3. Publish and qualify the ontology if formal authority is required.
4. Seek national source authority only if scope expansion is approved.
5. Advance beta, RC and stable gates independently; do not infer one from another.

No lane may be marked complete from local tests alone when its required
evidence is external or authority-bound.
