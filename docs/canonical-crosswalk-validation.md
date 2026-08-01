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
