# Python reference SDK (bounded conformance slice)

The `riopa_provenance.sdk` module provides deterministic producer-side
validation for the language-neutral conformance corpus:

- `canonical_instance_hash` uses the repository's canonical JSON hash;
- `validate_json_instance` applies Draft 2020-12 validation and returns a
  sorted, content-addressed `ValidationReport`;
- `validate_crosswalk` applies the bounded canonical crosswalk semantics,
  including fail-closed handling of uncertain mappings.

This is a local reference implementation for fixtures and repository-owned
checks. It is not a complete interoperability certificate, does not contact
source endpoints, and does not replace Rust, standards projections,
independent producer/consumer exercises, signed reports, or release authority.
