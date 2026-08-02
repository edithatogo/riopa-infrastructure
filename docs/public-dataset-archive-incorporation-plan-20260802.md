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

## Completed archive slice

Stats NZ Meshblock 2026 was captured in full by
[GitHub Actions run 30750165664](https://github.com/edithatogo/open_social_data/actions/runs/30750165664)
and published to the public
[Hugging Face archive](https://huggingface.co/datasets/edithatogo/riopa-public-data-archive).
The immutable packet revision is `3f2dc0a4d95a4fcb495551098d58fc5bce9c9202`;
the receipt-bearing revision is `34c093646f884d7b57447231d6605e83739bb302`.
The manifest records 57,575 of 57,575 object IDs across 231 pages, 16 null
geometries, a stable pre/post source inventory, manifest SHA-256
`1352a1693bba7dc6c090a56aedb89bd33c098985cde2bf3e74bd765990a19a5f` and
payload-set SHA-256
`706c6d39c497e643eb5989fc65d4824799d16ade197b4c808a4e2988722e9b14`.
Independent hosted readback verified the manifest and the first and final page
digests. RIOPA subsequently verified every stored and expanded archive object
and built 236 content-addressed capture records plus a normalized 57,575-feature
projection without contacting the recorded live endpoint. The projection
preserves 16 null geometries and one invalid translated source geometry without
implicit repair. Population tables and downstream analytical projections remain
pending; this supporting-geography projection is not national accessibility or
performance evidence.
