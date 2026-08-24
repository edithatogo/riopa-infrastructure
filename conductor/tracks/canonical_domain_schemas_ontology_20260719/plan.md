# Plan: canonical_domain_schemas_ontology_20260719

## 1. Evidence and identity inventory

- [x] 1.1 Inventory entities and identifiers across existing connector, archive, policy and health repositories. (`docs/canonical-domain-inventory-20260801.md`)
- [x] 1.2 Define identity, version identity, source assertion and adjudication rules. (`docs/canonical-domain-inventory-20260801.md`, `src/riopa_provenance/canonical.py`)
- [x] 1.3 Record unresolved semantic collisions and extension needs. (`docs/canonical-domain-inventory-20260801.md`)

## 2. Schema and ontology implementation

- [x] 2.1 Implement canonical JSON Schemas, JSON-LD contexts, SKOS concepts and SHACL shapes. (`schemas/canonical-crosswalk.schema.json`, `docs/ontology/canonical-context.jsonld`, `docs/ontology/canonical-ontology-release-1.0.0.json`; SHACL execution remains pending)
- [x] 2.2 Add bitemporal, original-value, confidence, review and governance fields. (`src/riopa_provenance/canonical.py`, `tests/test_canonical.py`)
- [x] 2.3 Generate language bindings and documentation. (`2a7cd96`; generated TypeScript declaration, drift test and bounded Python/Node golden-fixture parity)

## 3. Crosswalk and conformance

- [x] 3.1 Build council-planning, facility and source-service golden fixtures. (`fixtures/canonical-crosswalk-golden.json`, `conformance/v1/corpus.json`)
- [~] 3.2 Validate cross-language round trips and SHACL conformance. The bounded Python/Node parity receipt is preserved in `docs/ontology/canonical-cross-language-parity-20260824.json`; the dependency-free shape/property contract is implemented in `src/riopa_provenance/canonical.py` with negative tests, while SHACL engine evidence remains pending.
- [x] 3.3 Test identity under rename, reorganisation, relocation and supersession. (`tests/test_lineage_identifiers.py`, `tests/test_canonical.py`)

## 4. Stabilisation and migration

- [ ] 4.1 Run agent-panel semantic qualification and resolve semantic findings.
- [x] 4.2 Define the bounded migration compatibility and extension policy. (`docs/ontology/migrations/canonical-crosswalk-1.0.0-to-1.1.0.json`, `docs/ontology/canonical-extension-policy-20260825.json`, `docs/ontology/canonical-extension-policy-20260825.md`, `tests/test_canonical.py`; fail-closed policy validation passes, while execution qualification and stable publication remain open.)
- [ ] 4.3 Freeze the v1 normative schema/ontology candidate.

## Track closeout

- [ ] C.1 Link implementation, test, review, migration and release evidence in `index.md`.
- [ ] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [ ] C.4 Update metadata status and target-release evidence through the Conductor workflow.

## Review fixes

- [x] R.1 Add digest-bound SHACL shape preparation while preserving the
  `not-run` conformance status. (`1ac750a`)
- [x] R.2 Verify the updated manifest, ontology descriptor and tests under the
  project validation workflow. (`1ac750a`)
- [x] R.3 Correct the TypeScript binding documentation so hosted pytest drift
  enforcement and the equivalent local `--check` command are distinguished.
  (`913f683`; review fix)
