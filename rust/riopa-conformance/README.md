# Bounded Rust conformance model

This crate provides a dependency-free typed Rust model for the bounded
crosswalk and profile-migration contracts. It is intentionally small and
fail-closed: `Confidence::Unknown` requires an evidence reference.

Run it with:

```sh
cargo test --manifest-path rust/riopa-conformance/Cargo.toml --locked
```

The crate does not parse the JSON corpus, implement RFC 8785 canonicalisation,
or establish Rust/ Python corpus parity. Those remain separate interoperability
and external producer/consumer gates.
