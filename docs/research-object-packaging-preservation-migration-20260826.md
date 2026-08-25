# Research-object packaging, preservation and migration guidance

This guidance defines the repository-owned handoff for a bounded, public-source
technical-preview research object. It is an implementation guide, not a
publication or preservation receipt.

## Build the package

Use the locked Python 3.14 environment and build from a clean checkout:

```console
uv sync --locked --extra spatial --extra dev
uv run riopa validate --root .
uv run pytest -q
uv build --out-dir dist/package
bash scripts/build_sbom.sh dist/package/riopa-provenance.cdx.json
```

The package manifest, source/capture digests, methods, citation metadata,
quality reports, SBOM and `SHA256SUMS` must be retained together. A generated
artifact must never be replaced in place: create a new revision and preserve a
successor/correction record.

## Preserve and restore

Deposit the exact release packet, checksums and metadata to an approved
provider, then verify an anonymous restore against every digest. Record the
provider, immutable revision or DOI, transfer receipt and verification time in
the decision record. A Git commit or local build is not a preservation receipt.

## Migrate and correct

Consumers should pin the release revision and validate the manifest before
reading payloads. Corrections are append-only successor packets: retain the
superseded packet, explain the changed source or transformation, publish new
digests, and link the correction from the citation metadata. Do not mutate a
previously published packet or silently repair source-faithful records.

## Release boundary

This guidance does not create signed attestations, external reproduction,
provider acceptance, elapsed beta/RC evidence, national-scale evidence, or an
accountable release-authority decision. Until those facts are recorded, the
RIOPA scope remains a bounded regional, public-source, non-operational
technical preview.
