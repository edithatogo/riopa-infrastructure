# Materialisation Strategy

## Principle

A materialisation is an interface for a particular user or workload. It is not a new dataset with undocumented semantics.

## Format matrix

| Materialisation | Primary use | Strength | Known limits |
|---|---|---|---|
| Parquet | portable tabular analysis | compact, typed, cross-language | no native multi-table relationships |
| GeoParquet | portable vector spatial analysis | efficient geometry + columns | application support varies; topology not inherent |
| DuckDB | zero-server analytical bundle | joins, SQL, spatial extension, easy reuse | single-file concurrency/service limits |
| FlatGeobuf | streaming/download vector exchange | spatial index and efficient transfer | less rich dataset-level metadata |
| GeoJSON | small examples and debugging | ubiquitous and human-readable | large size, CRS limitations |
| PMTiles | public web maps | single-file tile distribution | visual/generalised view, not analytical truth |
| COG | raster distribution | range requests and GIS support | one asset/grid per file pattern |
| Zarr | chunked multidimensional arrays | cloud and parallel access | ecosystem/version complexity |
| STAC | catalogue and asset relationships | discoverability and spatiotemporal linking | catalogue, not storage format |
| PostGIS | deployed multi-user service | mature spatial DB and indexing | operational burden; not portable release |
| LanceDB | semantic/vector search over rules/documents | fast local/vector retrieval | derived index; embeddings and chunking are model-dependent |
| RDF/property graph | lineage and semantic queries | relationship-rich | storage/query complexity; easy to overproduce |

## Mandatory release forms

For vector/tabular spatial releases:

1. GeoParquet/Parquet distributions.
2. DuckDB analytical bundle with documented views.
3. JSON snapshot manifest and quality report.
4. RO-Crate metadata.

Additional formats are generated only when a user need is identified.

## Fidelity declaration

Every materialisation records:

- parent snapshot;
- selected entities/fields;
- filters and generalisation;
- CRS and geometry encoding;
- schema version;
- sort/partition/index strategy;
- null and type coercions;
- digest and size;
- reproducibility class;
- validation evidence.

## LanceDB boundary

LanceDB stores embeddings and retrieval metadata for plan text, provisions, source documents and perhaps facility descriptions. The canonical text, spans, model identity and chunking recipe remain outside the index. Deleting and rebuilding the index must not lose evidence.

## DuckDB bundle contract

The release DuckDB includes:

- read-only views over packaged Parquet/GeoParquet where practical;
- a `release_metadata` table with snapshot and schema identifiers;
- a `provenance_summary` view;
- a `quality_summary` view;
- example queries in `docs/queries/`;
- extension/version information and build provenance.
