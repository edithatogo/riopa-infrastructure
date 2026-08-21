# Canonical crosswalk TypeScript binding

`canonical-crosswalk-v1.d.ts` is generated from the normative
`schemas/canonical-crosswalk.schema.json` contract. Regenerate it with:

```sh
uv run python scripts/generate_canonical_bindings.py
```

The hosted test suite compares the generated output with the committed binding;
`--check` provides the equivalent local drift gate. The declaration preserves
required fields, nullable valid-time bounds and the complete confidence enum.
It does not perform runtime validation: consumers must validate input against
the JSON Schema and apply the semantic checks documented in
`docs/canonical-crosswalk-validation.md`.

`provenance-event-v1.d.ts` is the bounded TypeScript consumer model for the
normative provenance event schema. Runtime acceptance/rejection is performed
by `scripts/conformance_node.mjs` against the language-neutral corpus; this
surface is not a publication identifier, independent review, or signed
attestation.

The bounded Node runner independently checks the golden fixture's canonical
digest and structural schema outcome. This is non-Python binding and fixture
evidence; it is not a complete JSON Schema implementation, SHACL conformance,
an external-client qualification or a stable-v1 compatibility guarantee.
