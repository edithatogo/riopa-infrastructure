# Querying verified Tasman projections

Track: `nz_spatial_archive_mvp_20260718`; issue #49.

These examples read an **already restored and verified** derived packet. Live
acquisition, restoration and public verification remain in GitHub Actions;
running these examples does not download anything. Keep bulk files outside Git.
Use the pinned Python 3.14 environment with the `spatial` extra.

The [accepted derived packet](tasman-derived-acceptance-20260831.json) names
public revision `1ccd5953893c588f87a31fe77fcd3d6124f03fae`, its immutable prefix,
and trusted file checksums. The examples expect `packet` to point to its restored
directory and `accepted_files` to be that receipt's `publication_receipt.files`
mapping, not a manifest supplied by an unverified download. Verification of the
full packet, source lineage and rights remains the publication verifier's job.
Only the two exact spatial files are queried below; their sizes and checksums
are checked again immediately before use in a trusted, non-concurrently-mutated
directory. No extensions are installed or downloaded.

```python
import hashlib

import duckdb
import pyarrow.parquet as pq


def query_verified_projection(packet, accepted_files):
    if packet.is_symlink() or any(p.is_symlink() for p in packet.parents):
        raise ValueError("Projection directory must not be symlinked")
    paths = {}
    for name in ("features.parquet", "features.duckdb"):
        path = packet / name
        expected = accepted_files[name]
        if path.is_symlink() or not path.is_file():
            raise ValueError("Missing or symlinked projection")
        if path.stat().st_size != expected["bytes"]:
            raise ValueError("Projection size mismatch")
        with path.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        if digest != expected["sha256"]:
            raise ValueError("Projection digest mismatch")
        paths[name] = path
    table = pq.read_table(paths["features.parquet"])
    parquet_ids = sorted(str(value) for value in table["_riopa_source_object_id"].to_pylist())
    with duckdb.connect(str(paths["features.duckdb"]), read_only=True) as connection:
        connection.execute("SET enable_external_access=false")
        database_ids = [row[0] for row in connection.execute(
            "SELECT CAST(_riopa_source_object_id AS VARCHAR) FROM features ORDER BY 1"
        ).fetchall()]
        geometry_count = connection.execute(
            "SELECT COUNT(*) FROM features WHERE geometry IS NOT NULL"
        ).fetchone()[0]
    if parquet_ids != database_ids:
        raise ValueError("Cross-tool source identity mismatch")
    return {"feature_count": len(parquet_ids), "non_null_geometry_count": geometry_count}
```

Call `query_verified_projection(packet, accepted_files)`. The accepted Tasman
packet contains 3,655 features; the test fixture contains one synthetic polygon.
The test executes this exact code against the actual archive, public-packet and
two-rebuild producer chain with network/storage adapters replaced by fixtures.
It also rejects tampered and symlinked files before querying.

`_riopa_source_object_id` identifies a source object within this layer.
`_riopa_feature_id` and `_riopa_capture_ids` retain version/capture lineage;
they must not be treated as stable cross-capture join keys. Original projected
geometry is retained without implicit repair. These queries count geometry
presence, **not geometry validity**, area, topology or legal effect.

The canonical JSON's `canonical_features` records retain unknown valid time and
archive-recorded time separately. Neither a query nor a capture timestamp proves
operative planning status. CC-BY-4.0 and Tasman District Council (TDC) attribution
remain applicable. This is no claim of population denominators, source currency,
whole-track completion, scheduled change/recovery, external conformance or
isolated clean-room reproduction.
