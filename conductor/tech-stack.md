# Technology and Standards Stack

## Runtime and packaging

- Python 3.12 baseline for reference tooling and orchestration.
- Rust for high-throughput or safety-critical connectors where justified.
- `uv` lockfiles, reproducible containers and GitHub Actions.
- JSON Schema 2020-12 for cross-language contracts.

## Authoritative persistence

- Content-addressed raw objects with SHA-256 and optional stronger/multihash identifiers.
- Append-only JSONL/Parquet provenance event log.
- Immutable snapshot manifests with canonical JSON hashing.
- Git, software heritage identifiers, container digests and lockfile hashes for code identity.

## Portable data formats

| Data class | Primary portable form | Additional materialisations |
|---|---|---|
| Tabular | Parquet | CSV, DuckDB |
| Vector spatial | GeoParquet | DuckDB Spatial, FlatGeobuf, GeoJSON, PMTiles, PostGIS |
| Raster/gridded | COG or Zarr | STAC item/collection, tiles |
| Documents/web evidence | Original files, WARC/WACZ where appropriate | extracted text, PDF/A where lawful |
| Text/semantic | Parquet plus source spans | LanceDB/FAISS derived index |
| Provenance | JSON/JSONL and JSON-LD | RDF/PROV graph, OpenLineage events |

## Metadata and provenance profile

- W3C PROV-O: semantic entity/activity/agent model.
- OpenLineage: interoperable job/run/input/output event transport.
- RO-Crate 1.3: research-object packaging.
- Workflow Run RO-Crate profiles: workflow/run provenance packaging.
- in-toto Attestation Framework and SLSA 1.2: build and supply-chain evidence.
- DataCite 4.7: DOI metadata.
- DCAT 3, Croissant and Frictionless: catalogue and dataset metadata views.
- SPDX/CycloneDX and Sigstore: software bill of materials and signing/attestation.

## Geospatial profile

- NZGD2000/NZTM2000 retained where appropriate; WGS84 views generated for web interoperability.
- GeoParquet 1.1 baseline for vectors.
- STAC 1.1 for spatiotemporal assets and collections.
- OGC API Features and OGC API Records views where service publication is required.
- ISO 19157-1 concepts and W3C DQV for quality evidence.
- DuckDB Spatial for local analytical bundles; PostGIS optional for deployed services.

## Version axes

1. Code package SemVer.
2. Contract/schema SemVer.
3. Source-connector version.
4. Dataset snapshot CalVer plus content digest.
5. Ontology/classification version.
6. Model specification version.
7. Publication/research-object version and DOI.

No axis may be silently substituted for another.
