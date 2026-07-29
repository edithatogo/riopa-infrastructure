# Stable-v1 scope and responsibility boundaries

This document is the human-readable boundary contract for the foundation
architecture track. It complements the machine-readable track metadata and
release gates.

## Platform guarantees

RIOPA guarantees inspectable provenance events, immutable evidence references,
versioned contracts, deterministic validation, explicit uncertainty and
reproducible research-object construction when the declared input evidence and
environment are available.

## Separate release axes

Software, schemas/ontology, source datasets, analytical model specifications
and research objects are independently versioned. A release must identify the
exact version of each axis it contains; a software release does not imply a
dataset or model release.

## Responsibility boundaries

| Boundary | Authoritative responsibility | Explicit non-claim |
|---|---|---|
| Source registry and connectors | source identity, access policy and faithful raw capture | no canonical cross-source semantics |
| Archive orchestration | immutable snapshots, retention and preservation evidence | no source-specific network implementation |
| Canonical/domain packages | versioned entities, mappings and semantic contracts | no publication-only formatting |
| Materialisers | portable/query-optimised projections | no independent semantic truth |
| Quality/provenance | quality results, lineage and evidence references | no unrecorded manual override |
| Publication builder | research object, methods, citation and attestations | no scientific interpretation hidden in generation |
| Decision engines | explicit objectives, constraints, solutions and diagnostics | no legal, clinical or policy authority |
| Applied studies | bounded, citable analyses with stated limitations | no generalisation beyond their evidence |

## Non-claims

The platform does not claim legal authority for extracted planning meaning,
clinical authority for health analyses, completeness of any source catalogue,
or operational fitness without the corresponding release and evidence gates.
Restricted or sensitive material is never made public merely because it can be
captured or transformed.

## Compatibility and support boundary

The stable 1.x line preserves documented schemas, APIs, CLI behaviour,
configuration and file formats across compatible releases. Breaking semantic or
normative changes require a new major profile or software release and a
migration path. Stable support additionally requires named maintainers,
security response, preservation, conformance and annual revalidation evidence.
