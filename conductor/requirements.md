# Requirements

## Core provenance and reproducibility

- **R-001** Every captured source artifact has a stable identifier, retrieval timestamp, source locator, media type, byte size and cryptographic digest.
- **R-002** Every transformation run identifies code commit/SWHID, environment or container digest, lockfile digest, command, parameters, inputs, outputs and timing.
- **R-003** Every output artifact is traceable to source artifacts through one or more transformation activities.
- **R-004** Provenance is serialisable as the native event profile, W3C PROV-compatible JSON-LD and OpenLineage-compatible run events.
- **R-005** Build/release artifacts carry in-toto/SLSA-compatible attestations.
- **R-006** A release can generate a concise methods statement and a detailed supplementary methods package from the same evidence.
- **R-007** Provenance granularity is declared and never implies feature/row lineage that was not captured.

## Data and spatial requirements

- **R-010** Raw evidence, canonical datasets and materialisations are separate layers.
- **R-011** Canonical spatial vectors are publishable as GeoParquet and queryable in DuckDB Spatial.
- **R-012** Each spatial feature has source-layer identity, source-feature identity where available, geometry digest and bitemporal validity fields.
- **R-013** Plan spatial features can link to one or more source documents and legal provisions without asserting that extracted interpretations are authoritative.
- **R-014** Source, effective, retrieved, observed and superseded times remain distinguishable.
- **R-015** Raster and large spatiotemporal assets are catalogued through STAC-compatible metadata.
- **R-016** Quality reports cover completeness, validity, consistency, positional/temporal accuracy, uniqueness, lineage, rights and accessibility as applicable.

## Publication and reuse

- **R-020** Every snapshot has DataCite-ready metadata, citation text, source attributions and licence inventory.
- **R-021** Every release is packageable as an RO-Crate 1.3 research object.
- **R-022** Code, schema, dataset, ontology, model and publication versions are independent and explicit.
- **R-023** Portable flat files remain first-class even when database and index bundles are provided.
- **R-024** All materialisations declare deterministic derivation and can be regenerated.
- **R-025** The repository bootstrap creates or links a GitHub repository, project, labels, issues, sub-issues and dependencies from versioned configuration.

## Governance and safety

- **R-030** Public accessibility is not treated as permission to redistribute.
- **R-031** Every source and output carries a rights/redistribution status, including `unknown` where unresolved.
- **R-032** Māori data sovereignty assessment is performed for data for, from or about Māori and for derived products likely to affect Māori communities.
- **R-033** Health and social datasets begin with open aggregate data; use of sensitive or unit-record data requires a separate controlled-data architecture.
- **R-034** Optimisation outputs expose assumptions, uncertainty, subgroup impacts and normative weights.

## Reference implementation

- **R-040** The first implementation inventories all territorial and regional authorities and discovers their plan-data publication mechanisms.
- **R-041** A minimum viable council set demonstrates ArcGIS REST, WFS/Koordinates, static download and ePlan/document connectors.
- **R-042** LINZ, Stats NZ, Ministry for the Environment and Gazette/DigitalNZ source adapters are specified before full council scaling.
- **R-043** A supermarket/facility registry can reconcile multiple sources with confidence and conflict evidence.
- **R-044** Accessibility and facility-location engines accept interchangeable demand, candidate, network, capacity, equity and feasibility inputs.
- **R-045** Ambulance recommendations are evaluated in simulation before being described as operationally suitable.
