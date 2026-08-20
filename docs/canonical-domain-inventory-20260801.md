# Canonical domain identity and semantic inventory

This inventory records the repository-owned baseline for Conductor track
`canonical_domain_schemas_ontology_20260719`. It is a bounded implementation
inventory, not a claim that the ontology has domain-owner approval or published
SHACL/non-Python conformance.

## Entity and identifier coverage

| Domain object | Repository contract/evidence | Identity rule |
| --- | --- | --- |
| Authority, jurisdiction, service and endpoint | `schemas/source-record.schema.json`, canonical URN helpers and provenance validators | Stable RIOPA URN separates entity identity from version identity. |
| Facility and spatial feature | `schemas/spatial-feature-link.schema.json`, facility registry assertions and lineage fixtures | Source identifiers and original labels are retained; relocation creates a new version assertion. |
| Plan, provision and layer | `schemas/canonical-crosswalk.schema.json`, golden crosswalk fixture | Crosswalk claims retain source values, valid time, confidence and evidence. |
| Mapping, review and analytical run | Crosswalk semantics, governance decision and analysis protocol schemas | Unknown, disputed and inapplicable values remain distinct and fail closed without evidence. |

## Collision and extension register

- Source rename, reorganisation, relocation and supersession are represented
  as versioned assertions rather than silent identifier replacement.
- Council terminology is not collapsed into unsupported national equivalence;
  unresolved mappings remain disputed or unknown.
- Formal SHACL validation, a non-Python round trip and domain-owner review are
  still open gates in the conformance manifest.

## Evidence boundary

The structural and semantic Python validators and golden fixtures are passing.
They establish repository-owned contract behaviour only. They do not establish
external semantic authority, ontology publication, SHACL conformance or
cross-language compatibility.

