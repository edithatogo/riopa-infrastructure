# Architecture Overview

## Purpose

RIOPA Infrastructure is a federation of interoperable repositories rather than a monolith. A repository may implement only a connector, archive, schema, analytical engine, or publication layer and still participate if it emits and consumes the shared contracts.

## Component model

| Component | Inputs | Outputs | Must not own |
|---|---|---|---|
| Source registry | catalogues, service metadata, manual declarations | versioned source records and access policy | source payload transformation |
| Connector | source record, credentials/policy | raw objects, capture events, change evidence | canonical cross-source semantics |
| Archive orchestrator | connector outputs | immutable snapshots, mirror evidence, retention state | source-specific network code |
| Canonicaliser | raw objects, schemas, mappings | canonical entities and mapping evidence | publication-only formatting |
| Materialiser | canonical snapshot | portable/query-optimised formats | independent semantic truth |
| Quality engine | artifacts, schemas, source expectations | metric results and evidence | unrecorded manual overrides |
| Publication builder | snapshot, quality, provenance, metadata | research object, methods, citation, attestations | scientific interpretation |
| Decision engine | demand, candidates, networks, constraints, objectives | solutions, uncertainty and diagnostics | hidden policy weights |

## Recommended repository ecosystem

```text
riopa-infrastructure          shared profile, schemas, templates and programme
riopa-provenance              extracted reusable library once profile stabilises
nz-spatial-archive            reference orchestration and canonical snapshots
nz-spatial-connectors         optional connector collection or federated connector repos
riopa-location                domain-neutral location-allocation library
riopa-simulation              emergency/service simulation adapters
riopa-supermarket-health      applied study
riopa-emergency-access        applied ambulance/hospital study
```

The initial scaffold keeps shared reference code in one repository until boundaries are demonstrated by use. Extraction into multiple packages is a deliverable, not a starting assumption.

## Data-flow guarantees

### Capture guarantee

A connector emits a capture event only after raw bytes or a preservation reference are available and hashed. HTTP success alone is not a successful capture.

### Transformation guarantee

A transformation event is complete only when all declared outputs are present, hashed and schema-validated, or the run is explicitly marked failed/partial with diagnostics.

### Snapshot guarantee

A snapshot manifest is immutable once released. Corrections create a successor and record `is_revision_of`, reasons and affected entities/partitions.

### Publication guarantee

The human methods text, citation metadata and quality summary are generated from the release manifest. Editorial additions may be layered on but cannot alter recorded facts without changing the manifest.

## Identity model

Use URIs or URNs as logical identifiers. Recommended patterns:

```text
urn:riopa:source:<registry-key>
urn:riopa:capture:<uuidv7>
urn:riopa:artifact:sha256:<digest>
urn:riopa:run:<uuidv7>
urn:riopa:snapshot:<dataset-key>:<calver>:<manifest-prefix>
urn:riopa:feature:<namespace>:<stable-key>
urn:riopa:provision:<jurisdiction>:<plan>:<version>:<path>
urn:riopa:materialization:<snapshot-id>:<format>:<variant>
```

External persistent identifiers such as DOI, SWHID, ORCID, ROR, RAiD and NZBN are retained as identifiers, not copied into a new namespace.

## Event integrity

Each event includes:

- canonical event hash;
- optional previous-event hash within a stream;
- producer identity and software version;
- recorded and occurred timestamps;
- references to input/output artifact digests;
- signature/attestation references where available.

Hash chaining detects local mutation. Signed in-toto/SLSA attestations provide stronger release/build claims. Neither replaces preservation, source metadata or semantic lineage.

## Query architecture

The MVP ships a DuckDB bundle containing relational projections:

- `sources`
- `captures`
- `artifacts`
- `runs`
- `run_inputs`
- `run_outputs`
- `snapshots`
- `materializations`
- `quality_results`
- `feature_versions`
- `provision_links`

An RDF/PROV graph is emitted for interoperability. A dedicated graph database is optional and justified only by query volume or graph-native applications.

## Deployment profiles

### Local research profile

GeoParquet/Parquet + DuckDB + RO-Crate. No server required.

### Public catalogue profile

Object storage + STAC/OGC API Records + static documentation + DOI releases.

### Service profile

Object storage + PostGIS or DuckDB service + OGC APIs + authentication/rate limits.

### Controlled-data profile

Separate architecture with approved compute, access controls, audit and disclosure review. It is not an extension flag on the public profile.
