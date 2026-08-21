# Canonical cross-language fixture

`fixtures/canonical-crosswalk-golden.json` is the frozen semantic fixture for
cross-language implementations. Python verifies its JSON Schema and RFC 8785
canonical JSON digest. The bounded Node standard-library runner independently
reproduces that digest and structural schema outcome through
`conformance/v1/corpus.json`.

The generated TypeScript declaration in `bindings/typescript/` binds the same
required fields, valid-time nullability and confidence enum. This demonstrates
a bounded non-Python binding and golden-fixture round trip. It does not claim a
complete JSON Schema implementation, SHACL conformance, external-client
qualification or stable-v1 compatibility.
