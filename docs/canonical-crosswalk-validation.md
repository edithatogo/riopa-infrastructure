# Canonical crosswalk validation

`schemas/canonical-crosswalk.schema.json` defines the structural contract. The
`validate_crosswalk_semantics` helper adds fail-closed checks that JSON Schema
cannot express portably: valid-time ordering and mandatory evidence for
unknown, disputed or inapplicable mappings. A non-empty error tuple means the
claim must not be promoted or treated as an accepted equivalence.

`validate_crosswalk_contract` combines required-field, identifier, source
assertion and semantic checks without optional validator dependencies. It is a
structural gate, not a SHACL conformance claim; full SHACL and cross-runtime
validation remain future evidence requirements.

`validate_bounded_shacl_constraints` checks the published Crosswalk shape's
target and required property declarations and applies that small declaration
set to a JSON crosswalk record. This protects against shape drift without
introducing an RDF dependency or claiming that the repository contains a full
SHACL processor. The conformance manifest therefore remains `bounded-pending`
until a real SHACL runtime produces an immutable report.

The versioned migration fixture under `docs/ontology/migrations/` is a
machine-readable compatibility example. It records retained source values and
the evidence constraint; it does not establish support for any non-Python
runtime until independently reproduced.
