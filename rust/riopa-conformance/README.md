# Bounded Rust conformance model

This crate provides a typed Rust model and a bounded canonical-hash runner for
the crosswalk, profile-migration and checked-in corpus contracts. It remains
small and fail-closed: `Confidence::Unknown` requires an evidence reference.

Run it with:

```sh
cargo test --manifest-path rust/riopa-conformance/Cargo.toml --locked
cargo run --manifest-path rust/riopa-conformance/Cargo.toml --locked --bin conformance_corpus
```

The corpus runner sorts object keys recursively and matches the five checked-in
canonical SHA-256 fixtures. Schema-validity parity, full RFC 8785 numeric
canonicalisation, independent external producer/consumer implementation and
signed release conformance remain separate gates.
