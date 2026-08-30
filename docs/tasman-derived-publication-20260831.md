# Tasman derived-output preservation

Track: `nz_spatial_archive_mvp_20260718`, task 3.7, issue #49.

The `Publish and rebuild licensed Tasman archive` workflow extends the existing
rights-qualified source-packet publication with public preservation of its
canonical records, GeoParquet and DuckDB projections. Live acquisition and
publication run on GitHub Actions; local tests use fixtures. Bulk outputs do not
enter Git or the metadata-only Actions artifact.

The source packet remains the immutable authority for capture identity and
captured rights. Derived outputs retain CC-BY-4.0, Tasman District Council
attribution, capture lineage, unknown valid time and non-authoritative legal
status. They are translated projections, not original source bytes. The mixed
catalogue and website packet is not included.

## Acceptance contract

- Verify the source packet and both local rebuilds before publishing a fixed
  allowlist of outputs; do not publish a directory glob.
- Bind the public manifest to the source revision, source manifest digest,
  rights, projection contract and actual file sizes/checksums.
- Commit the complete derived packet atomically; retain a durable checkpoint.
- Download from the exact public revision without credentials, using bounded
  parallelism, and verify file closure, bytes and spatial semantic readback.
- Preserve the first accepted physical DuckDB file. Its file bytes can differ
  across equivalent rebuilds: compare semantic identity on replay and reuse
  the original revision, rather than silently replacing it.
- Recover a publication/checkpoint interruption only after verifying the
  existing immutable packet. Preserve sanitized failed-attempt evidence and
  never mark a failed readback as acceptance.

## Scope boundary

The derived packet has exactly four files: `canonical.json` (full projected
attributes/WKB plus the original canonical identity/lineage/time records),
`features.parquet`, `features.duckdb`, and `manifest.json`. The manifest contains
the three payload checksums; the durable checkpoint binds the manifest's byte
checksum and immutable public revision. A versioned profile and publisher-code
digest participate in the logical identity. Anonymous payload downloads use
three workers. The receipt is `public/tasman-derivatives.json`.

The isolated advisory reviewer checked source/provenance and rights bindings,
actual payload readback, immutable replay, failure evidence and workflow
ordering. Review corrected the DuckDB external-access ordering and ensured the
local failure artifact reflects a failed durable-evidence write. The pinned
DuckDB runtime supports the required spatial function without loading another
extension; external access is disabled before querying. Fourteen new tests
(plus the workflow test), strict MyPy, Ruff and Bandit pass locally. The tests
include an actual fixture archive/projection round trip and a physically
different fresh DuckDB file with equivalent feature semantics.

Hosted acceptance and replay must be recorded separately after execution.
Implementation or local tests alone do not prove publication. Manual replay is
not a scheduled change/recovery cycle or isolated clean-room agent reproduction.
This task does not close the whole archive track, establish operative planning
status, supply population denominators, or advance a release gate.

## Hosted result

`docs/tasman-derived-acceptance-20260831.json` records successful Actions run
33335595270 attempts 1 and 2 on merged implementation `9f262b7`. Both verified
the same immutable derived revision, with byte-identical acceptance receipts.
This supplies the publication/replay evidence required above; the scope
boundaries still apply.
