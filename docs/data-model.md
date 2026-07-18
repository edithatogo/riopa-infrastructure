# Canonical Data Model

## Core entities

### Source

A logical publisher/product/service. It contains jurisdiction, publisher, access mechanism, licence and governance metadata but no mutable payload state.

### Source version

A versioned metadata state for a source or service definition, including service capabilities, layer schema, publication metadata and digest.

### Capture

An activity that retrieves or references source bytes under a declared policy.

### Artifact

A content-addressed file/object or resolvable preservation reference. Content identity and logical identity are separate.

### Transformation run

An activity that consumes artifacts and produces artifacts or canonical entity versions.

### Dataset snapshot

An immutable logical selection of canonical entity versions, schemas and provenance closure.

### Materialisation

A physical representation of a snapshot, such as GeoParquet, DuckDB, PMTiles or LanceDB.

### Quality assertion

A metric or assessment with method, result, threshold, status and evidence.

## Spatial/legal entities

### Spatial feature version

```text
feature_id                  stable logical identity
feature_version_id          immutable version identity
feature_type                zone, overlay, precinct, designation, parcel, facility...
source_feature_id           publisher identifier when stable
source_layer_id             versioned source layer
geometry                    canonical geometry
geometry_sha256             canonical geometry digest
properties                  source-preserving and canonical properties
valid_from / valid_to       represented-world/legal interval
recorded_from / recorded_to infrastructure knowledge interval
status_assertions[]         sourced status, confidence and time
```

### Plan and provision

```text
plan_id, plan_version_id
publisher, jurisdiction
plan_status assertions
source documents and captures
provision_id                 stable path/citation identity
provision_version_id
heading, text spans, source page/fragment
valid and recorded intervals
```

### Spatial-rule link

A many-to-many evidence object linking a feature version to provisions. It records the link method (`publisher-provided`, `deterministic identifier`, `rule-based`, `model-assisted`, `manual`), confidence, reviewer, evidence and caveats.

### Facility

A reconciled logical place/service with source records retained separately. Facility identity does not overwrite source identity.

```text
facility_id
facility_type and classification version
name variants
location versions and positional confidence
operator/organisation links
opening/service availability assertions
source records and match evidence
valid/recorded intervals
rights constraints
```

## Snapshot tables

Recommended local DuckDB tables:

```text
catalog.sources
catalog.source_versions
provenance.events
provenance.artifacts
provenance.activities
provenance.activity_inputs
provenance.activity_outputs
snapshots.snapshots
snapshots.materializations
quality.results
spatial.feature_versions
spatial.feature_status_assertions
planning.plan_versions
planning.provision_versions
planning.spatial_rule_links
facilities.facilities
facilities.source_records
facilities.match_candidates
```

## Canonicalisation rules

- Preserve source fields in a namespaced structure or source table.
- Canonical fields carry mapping rule and version.
- Never overwrite a source coordinate with a geocoded coordinate; store both assertions.
- Geometry repair produces a derived geometry and records the repair algorithm and changed topology/area metrics.
- Text normalisation retains source byte/character spans where possible.
- Aggregation stores denominator, membership definition and suppressed/missing categories.

## Schema evolution

- Backward-compatible additions: minor version.
- Meaning, cardinality or identifier changes: major version.
- Corrections to examples/constraints without data effect: patch version.
- Every migration is an executable, provenance-emitting transformation.
