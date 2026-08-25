# Interoperability v1 SDK support and conformance reporting

This document freezes the repository-owned support surface for the bounded
technical preview and explains how a future conformance report must be built.

## Supported surfaces

The Python surface is `riopa_provenance.sdk` and is limited to canonical hash,
Draft 2020-12 instance validation, and the bounded canonical crosswalk. The
Rust surface is the typed model and bounded canonical-hash runner under
`rust/riopa-conformance`; its supported commands are the locked Cargo test and
`conformance_corpus` commands in that crate's README. Both surfaces are fixture-oriented and must
preserve unknown or uncertain mappings rather than silently upgrading them.

Support ownership for this repository is the single maintainer. Agent-panel
lenses may review evidence and propose findings, but they are not external
implementations, independent operators, or release authorities.

## Compatibility rules

Consumers should pin the contract and corpus versions, reject unknown major
profile versions, and retain the declared evidence references. A change to
hashing, validation semantics, wire fields, or confidence interpretation is a
breaking change and needs a new version plus migration evidence. Additive
optional fields are compatible only when older consumers can safely ignore
them without semantic loss.

## Conformance report template

A signed report, when the signing and release gates are available, must include
the exact repository commit, corpus digest, tool versions, command lines,
positive and negative results, semantic-loss findings, and signer/accountable
authority. Until then, this document and the bounded local/hosted checks are
unsigned repository evidence only. External producer/consumer reproduction,
standards-complete serialization, trusted signing, preservation acceptance,
and beta/RC/stable promotion remain open.
