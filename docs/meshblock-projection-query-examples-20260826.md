# Archived Meshblock projection query examples

These examples are a read-only interface contract for the content-addressed
Stats NZ Meshblock projection. They are illustrative SQL, not a claim that the
bulk GeoParquet or DuckDB files are present in this Git checkout.

## Input and identity contract

Restore the bulk products from the immutable packet identified by
`evidence/stats-nz-meshblock-2026-projection/records-manifest.json`. Before
querying, verify the materialization receipt and require this projection ID:

```text
urn:riopa:projection:sha256:64a1cbce366794b2b802f04dbe2bf1dc5fbf813e5c5b159bcf0782af9adc511f
```

The packet revision is `3f2dc0a4d95a4fcb495551098d58fc5bce9c9202` and the
projection uses EPSG:2193 with `OBJECTID` as its feature identifier. Queries
must use the restored packet bytes and must not contact the live ArcGIS URL.

## DuckDB / GeoParquet examples

Set `projection_path` to the verified local restore of the GeoParquet file.
Every connection is read-only:

```sql
-- feature and identifier inventory
SELECT count(*) AS feature_count,
       count(DISTINCT OBJECTID) AS distinct_object_ids
FROM read_parquet($projection_path);

-- preserved null geometries (no implicit repair)
SELECT count(*) AS null_geometry_count
FROM read_parquet($projection_path)
WHERE geometry IS NULL;

-- bounded lineage inspection
SELECT OBJECTID, capture_record_id, source_geometry_sha256
FROM read_parquet($projection_path)
ORDER BY OBJECTID
LIMIT 20;
```

The exact column names and physical format must be checked against the restored
artifact schema before execution; these examples intentionally do not infer
population, accessibility, facilities, network, timetable, national
completeness, or operational authority.

## Evidence boundary

Successful query execution demonstrates only readback of a restored,
revision-addressed projection. It does not satisfy bulk-artifact restoration by
an independent target, external operator reproduction, national completeness or authority,
preservation-provider acceptance, or accountable release approval. Those gates
remain fail-closed until their factual evidence is recorded.
