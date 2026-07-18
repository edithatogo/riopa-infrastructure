# RIOPA Standards Profile v0.1

This profile selects a small internal model and defines loss-aware mappings to established standards. It does not attempt to merge every external vocabulary into one schema.

## Normative baseline

| Concern | Standard/profile | RIOPA use | Requirement |
|---|---|---|---|
| Semantic provenance | [W3C PROV-O](https://www.w3.org/TR/prov-o/) | Entity, Activity, Agent and derivation semantics | Required mapping |
| Operational lineage | [OpenLineage](https://openlineage.io/docs/) | Job/run/input/output events and custom RIOPA facets | Required adapter for workflows |
| Research packaging | [RO-Crate 1.3](https://w3id.org/ro/crate/1.3) | Root dataset, people, organisations, software, files and contextual entities | Required for releases |
| Workflow execution | [Workflow Run RO-Crate profiles](https://www.researchobject.org/workflow-run-crate/) | Process/workflow/provenance run representation | Required where a workflow is published |
| Supply-chain evidence | [in-toto Attestation Framework](https://github.com/in-toto/attestation) and [SLSA 1.2](https://slsa.dev/spec/v1.2/) | Build and source provenance, signed release attestations | Required for releases when supported |
| Citation metadata | [DataCite Metadata Schema 4.7](https://schema.datacite.org/meta/kernel-4/) | DOI-ready metadata and related identifiers | Required release view |
| Data catalogue | [DCAT 3](https://www.w3.org/TR/vocab-dcat-3/) | Dataset/distribution catalogue interoperability | Required public-catalogue view |
| ML/data tooling | [Croissant](https://mlcommons.org/working-groups/data/croissant/) | Machine-actionable dataset view where useful | Recommended |
| Tabular packaging | [Frictionless Data](https://specs.frictionlessdata.io/) | Resource/schema view for simple tabular consumers | Recommended |
| Vector spatial | [GeoParquet 1.1](https://geoparquet.org/releases/v1.1.0/) | Canonical portable vector distributions | Required for vector releases |
| Spatiotemporal assets | [STAC 1.1](https://github.com/radiantearth/stac-spec) | Collections/items/assets for raster and large spatial outputs | Required when applicable |
| Feature services | [OGC API Features](https://ogcapi.ogc.org/features/) | Optional standards-based service view | Optional |
| Catalogue services | [OGC API Records](https://ogcapi.ogc.org/records/) | Public discovery API | Recommended for service profile |
| Geospatial quality | [ISO 19157-1:2023](https://www.iso.org/standard/78900.html) concepts | Quality dimensions and evaluation reporting | Required conceptual alignment |
| Data quality vocabulary | [W3C DQV](https://www.w3.org/TR/vocab-dqv/) | Machine-readable quality metrics and annotations | Required mapping |
| Software identity | [Software Heritage persistent identifiers](https://docs.softwareheritage.org/devel/swh-model/persistent-identifiers.html) | Code snapshot identity | Recommended |
| SBOM | SPDX or CycloneDX | Dependency and component inventory | Required release artifact |

## Version policy

- Pin the profile to named external versions at release time.
- Accept compatible newer patch/minor versions only after automated mapping tests.
- Record the exact `conformsTo` URIs in each research object.
- Do not silently rewrite old releases when an external standard changes.

## Core-to-PROV mapping

| RIOPA | PROV-O |
|---|---|
| artifact, source version, snapshot, materialisation | `prov:Entity` |
| capture, transformation, validation, publication | `prov:Activity` |
| person, organisation, software agent, service | `prov:Agent` or qualified agent entity |
| input to run | `prov:used` |
| output from run | `prov:wasGeneratedBy` |
| transformed/successor entity | `prov:wasDerivedFrom` |
| responsible software/person | `prov:wasAssociatedWith` |
| source attribution | `prov:wasAttributedTo` |
| revision | `prov:wasRevisionOf` |
| invalidation/supersession | `prov:wasInvalidatedBy` plus temporal fields |

## OpenLineage facets

RIOPA custom facets use a resolvable namespace such as:

```text
https://w3id.org/riopa/openlineage/source-rights-facet/v1
https://w3id.org/riopa/openlineage/bitemporal-facet/v1
https://w3id.org/riopa/openlineage/quality-evidence-facet/v1
https://w3id.org/riopa/openlineage/research-object-facet/v1
```

Custom facets are projections over the core event; they are not separately authored.

## RO-Crate profile additions

A RIOPA release crate includes:

- root `Dataset` with snapshot and schema versions;
- `CreateAction`/workflow-run entities for transformations;
- source artifacts or resolvable references;
- software and environment entities;
- quality report and rights inventory;
- spatial/temporal coverage;
- DataCite and DCAT metadata files;
- methods and citation files;
- checksums, SBOM and attestations.

## Compatibility rule

The internal profile may carry more detail than an export standard. Adapters must declare:

- fields mapped exactly;
- fields mapped approximately;
- fields omitted;
- any semantic loss.
