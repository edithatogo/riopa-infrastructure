# Experimental archived capture view migration

## Contract decision

This is a bounded implementation amendment to ADR-0002 (native provenance is
preserved) and ADR-0008 (independently versioned contracts). It adds an opt-in
`archived_capture_view/1.1.0` representation over the existing
`archived_http_capture/1.0.0` wrapper used by the archived Stats NZ packet.
The target schema is `schemas/archived-capture-view.schema.json`.

It does not change `schemas/provenance-event.schema.json`, announce a stable
provenance-event 1.1 release, or turn the old declarative profile migration
fixture into a claim of full event migration. This is an experimental native
adapter under provenance R05, with one real archived source family exercised.
Its version is independent of event-schema and software-package versions.

## Compatibility and mapping

| Native field | View mapping | Recovery |
|---|---|---|
| `capture_id` | `source.capture_id`, exact | Original identity restored |
| `record_sha256` | `source.record_sha256`, exact | Original digest restored and verified |
| `record`, including unrecognised native extensions | `source.record`, exact recursive copy | Every original field retained |
| Optional quality/rights evidence | `facets.quality` / `facets.source_rights`, URI plus SHA-256 references | View-only annotations, not injected into the native record |
| New view integrity | `view_sha256`, RFC 8785 hash of all fields except itself | Checked before recovery |

Native capture hashes are verified before conversion or recovery. Source identity
must match that hash. A view hash cannot repair an invalid native hash. Facet
references are declarations only: this API checks their structure, not their
contents, applicability or authority. Omit absent evidence; never fabricate a
rights decision or quality assessment. Field mapping is exact for the native
record; new view-only annotations have no native equivalent.

Old consumers continue to read unchanged native 1.0 records. They must not be
sent the new wrapper. `recover_capture` supplies the original logical record;
the untouched original file remains the source for byte-exact retrieval,
signature verification and archival formatting. No old representation is removed
or deprecated by this change.

## Usage and recovery

Use `migrate_capture(source, facets=...)` and `recover_capture(view)` for logical
records. `migrate_capture_jsonl(source_path, destination)` validates the entire
batch before atomically creating a separate destination. Equal existing bytes
are an idempotent retry; conflicting bytes fail. The destination directory must
exist. This bounded in-memory adapter is intended for small receipt batches,
not national bulk payloads or a production disaster-recovery claim.

A malformed row or duplicate JSON key aborts the batch. An interrupted final
publication leaves no partial destination; the source remains intact and the
same invocation can be retried. The adapter never upgrades the source in place.

Reproduce the recorded real-input migration with:

```bash
uv run python -m scripts.build_capture_migration_evidence --root . --output /tmp/capture-migration.json
```

Compare it with `docs/archived-capture-migration-evidence-20260912.json`.
All 236 archived national capture records validate against the target schema,
round-trip to equal native objects, and retain the original source file hash.
The receipt includes source/schema/output hashes and the matching before/after
canonical record-list hashes. Derived output is temporary and is not published.

## Qualification boundary

This supplies one real-input migration/recovery example for foundation M3 and
provenance R05. Broader native adapters, event-profile migration, non-Python
round-trip, exact-candidate panel disposition and M4–M6 gates remain open.
Foundation and provenance remain validating/M2. The scheduled campaign has not
run after PR #774 as of this inspection, so hosted ledger recovery is unverified.

Validation: 2,000 tests passed, one skipped; branch-aware coverage 90.71%.
All 23 focused migration cases passed. `scripts/ci_quality.sh`,
`scripts/ci_reproducibility.sh` and roadmap validation passed. The dated
`docs/module-coverage-inventory-20260912.json` records the updated module set;
the earlier hash-bound inventory remains unchanged.
