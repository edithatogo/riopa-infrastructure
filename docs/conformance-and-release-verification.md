# Conformance and release verification

## Language-neutral corpus

`conformance/v1/corpus.json` is data, not Python test code. Each case binds:

- a JSON instance;
- its expected RFC 8785 canonical SHA-256;
- an optional repository schema; and
- the expected schema outcome.

The Python reference implementation and `scripts/conformance_node.mjs` consume
the same corpus independently. The Node runner uses only its standard library
and implements the schema keywords exercised by the current corpus. It must not
be described as a complete JSON Schema implementation. Expand its supported
keywords, or use a separately maintained full validator, before adding fixtures
that exercise other keywords.

Run both implementations with:

```sh
uv run pytest tests/test_conformance.py
node scripts/conformance_node.mjs conformance/v1/corpus.json
```

The current corpus proves a bounded cross-language canonical-hash and schema
outcome contract. It does not yet satisfy the track-wide Rust, standards
projection, SDK, external-client, or signed-report criteria.

## Release attestations

The protected-tag release workflow builds assets without write credentials,
checks their checksum inventory, and uploads an immutable candidate. Its
environment-gated publish job registers GitHub artifact attestations for the
wheel, source distribution, research-object archive, CycloneDX SBOM, and
`SHA256SUMS`. It then independently invokes `gh attestation verify` for every
subject before creating the GitHub release.

For a published asset, an external verifier can use:

```sh
gh attestation verify PATH_TO_ASSET --repo edithatogo/riopa-infrastructure
sha256sum --check SHA256SUMS
```

The workflow proves authenticated build provenance only after it has run for a
protected tag. Configuration and local tests are not a signed release, an
independent scientific review, or preservation in a separate failure domain.
