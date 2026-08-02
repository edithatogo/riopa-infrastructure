# Public dataset archive and incorporation plan

RIOPA will not analyse mutable live endpoints directly. Every selected public
dataset first becomes a versioned archive packet containing source authority,
exact version or observation time, terms, retrieval receipts, completeness or
page dispositions and SHA-256 digests. Canonical, Parquet, GeoParquet, DuckDB,
network, facility and benchmark projections must identify that archived packet.

## Cross-repository routing

- `open_social_data` owns public provider acquisition work for Stats NZ
  geography/population ([#35](https://github.com/edithatogo/open_social_data/issues/35)),
  public food-retail assertions ([#36](https://github.com/edithatogo/open_social_data/issues/36))
  and NZTA/network/GTFS sources ([#37](https://github.com/edithatogo/open_social_data/issues/37)).
- `corpus-legislation-nz` already owns Gazette archive and freshness work in
  [#143](https://github.com/edithatogo/corpus-legislation-nz/issues/143) and
  [#144](https://github.com/edithatogo/corpus-legislation-nz/issues/144), so no
  duplicate issue was created.
- `healthpoint-rs` [#52](https://github.com/edithatogo/healthpoint-rs/issues/52)
  remains a code-first contract adapter. Licensed Healthpoint payloads are not
  part of this public-only campaign.
- The planned `nz-spatial-archive` repository does not yet exist. This
  repository therefore retains archive-plan ownership until a content-bound
  handover is possible.

## Incorporation order

1. Freeze source metadata, version and rights/terms.
2. Capture raw bytes or every bounded page, preserving failures and omissions.
3. Validate completeness and calculate immutable digests.
4. Preserve the raw packet outside Git when it is bulk data; commit only safe
   manifests, receipts and bounded evidence.
5. Build source-specific normalized/materialized projections.
6. Incorporate named projections into registry, archive, accessibility,
   facility, planning and performance tracks.
7. Run an agent-panel review of provenance, completeness, limitations and
   claims before any maturity change.

The machine-readable plan lists the exact source families, routing, status,
downstream tracks and non-claims in
`docs/public-dataset-archive-incorporation-plan-20260802.json`.
