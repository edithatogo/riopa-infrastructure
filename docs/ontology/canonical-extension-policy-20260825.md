# Canonical extension policy (bounded draft)

This policy defines how the canonical crosswalk carries fields that are not
yet normative. It is intentionally fail-closed and applies only to the
repository-owned bounded profile; it does not establish a published ontology
or stable compatibility guarantee.

1. Extension keys use versioned absolute URI namespaces, for example
   `https://w3id.org/riopa/extension/example/v1`.
2. Unknown extension values are preserved in the `extensions` object and are
   never silently promoted to normative fields.
3. An extension cannot redefine, shadow or change the meaning of a normative
   path.
4. Any schema or semantic change requires a versioned migration fixture and an
   explicit compatibility classification before release consideration.
5. Malformed, unnamespaced or conflicting extensions fail validation.

The machine-readable contract is
`canonical-extension-policy-20260825.json`. SHACL execution, publication,
semantic panel qualification and migration compatibility execution remain open
gates.
