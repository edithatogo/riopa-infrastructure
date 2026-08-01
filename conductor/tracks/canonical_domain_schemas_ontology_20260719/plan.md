# Plan: canonical_domain_schemas_ontology_20260719

## 1. Evidence and identity inventory

- [x] 1.1 Inventory entities and identifiers across existing connector, archive, policy and health repositories. (`docs/canonical-domain-inventory-20260801.md`)
- [x] 1.2 Define identity, version identity, source assertion and adjudication rules. (`docs/canonical-domain-inventory-20260801.md`, `src/riopa_provenance/canonical.py`)
- [x] 1.3 Record unresolved semantic collisions and extension needs. (`docs/canonical-domain-inventory-20260801.md`)

## 2. Schema and ontology implementation

- [ ] 2.1 Implement canonical JSON Schemas, JSON-LD contexts, SKOS concepts and SHACL shapes.
- [ ] 2.2 Add bitemporal, original-value, confidence, review and governance fields.
- [ ] 2.3 Generate language bindings and documentation.

## 3. Crosswalk and conformance

- [ ] 3.1 Build council-planning, facility and source-service golden fixtures.
- [ ] 3.2 Validate cross-language round trips and SHACL conformance.
- [ ] 3.3 Test identity under rename, reorganisation, relocation and supersession.

## 4. Stabilisation and migration

- [ ] 4.1 Run public review and resolve semantic findings.
- [ ] 4.2 Publish migration tools, compatibility matrix and extension policy.
- [ ] 4.3 Freeze the v1 normative schema/ontology candidate.

## Track closeout

- [ ] C.1 Link implementation, test, review, migration and release evidence in `index.md`.
- [ ] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [ ] C.4 Update metadata status and target-release evidence through the Conductor workflow.
