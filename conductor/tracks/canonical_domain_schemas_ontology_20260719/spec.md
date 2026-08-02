# Track: Canonical domain schemas, identifiers and ontology

Track ID: `canonical_domain_schemas_ontology_20260719`  
Phase: **Core**  
Target release: **0.3.0**  
Maturity target: **M6**  
Stability class: **Normative**  
V1 critical: **yes**

## Goal

Define stable, versioned identities and semantics for authorities, services, plans, provisions, spatial features, facilities, assertions, mappings and analytical runs.

## v1 role

This track is part of the stable v1 release contract. It is complete only when its implementation, compatibility, quality, security/governance, operational and reproducibility evidence satisfy both this specification and every applicable blocking gate in `conductor/releases.json` and `conductor/v1-gate.json`.

## Dependencies


- `foundation_architecture_20260718`

## Scope

- Canonical JSON Schemas and SHACL shapes for core domain entities.
- SKOS/JSON-LD ontology concepts and versioned crosswalks.
- Stable identifier, identity-resolution, bitemporal and provenance attachment rules.
- Original-value preservation, mapping confidence, disagreement and human adjudication.
- Schema/ontology migrations, compatibility fixtures and generated language bindings.

## Out of scope

- Collapsing distinct council meanings into one unsupported national equivalence.
- Replacing source vocabularies or legal text with the canonical ontology.

## Requirements

- **R01.** Canonical records retain original labels, identifiers, source assertions and evidence.
- **R02.** Identity and version identity are separate for changeable entities.
- **R03.** Crosswalks are versioned claims with method, confidence, reviewer and valid time.
- **R04.** Unknown, disputed and inapplicable values remain distinguishable.
- **R05.** Normative schemas carry stable identifiers and machine-readable migration metadata.

## Acceptance criteria

- [ ] Schemas cover authority, jurisdiction, service, endpoint, layer, plan, provision, feature/version, facility/assertion, mapping, review and analytical run.
- [ ] A versioned ontology and SHACL validation suite are published with original-to-canonical crosswalk fixtures.
- [ ] Identifier rules survive source renames, authority reorganisation, facility relocation and plan replacement.
- [ ] Python and Rust or another non-Python binding round-trip golden fixtures without semantic loss.
- [ ] At least two heterogeneous council and two facility-source examples validate the model.
- [ ] Stable 1.x schema and ontology migration rules pass backward-compatibility tests.

## Hardening and maturity gates

- M2 requires executable proof, negative tests and traceable evidence; interfaces may remain experimental.
- M3 requires real-data integration, migration evidence and representative failure handling.
- M4 requires repeated operation, external use, SLO evidence and bounded compatibility changes.
- M5 requires frozen interfaces, orchestrated agent-panel qualification, security/performance/recovery qualification and release-candidate soak.
- M6 requires supported compatibility, signed and preserved releases, external reproduction, named maintainers and post-release verification.
- Exceptions must be machine-readable, scoped, approved, time-limited and visible in release evidence.

## Evidence required

- Normative schema and ontology releases.
- Identifier and crosswalk specification.
- Golden fixtures, SHACL reports and cross-language round trips.
- Migration matrix and semantic-difference register.

## Risks

- Ontology ambition delays real vertical slices.
- Stable IDs depend on mutable names or coordinates.
- Mappings imply certainty or legal equivalence not supported by evidence.
- Generated bindings diverge from JSON Schema meaning.

## Completion rule

The track may enter `complete` only after every acceptance criterion is evidenced in `index.md`, all blocking dependencies are complete, required migrations and documentation are published, and the target release readiness evaluator reports no track-specific blocker.
