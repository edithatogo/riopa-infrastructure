# Release Verification

## Offline and CI Verification Commands

Releases include reproducible SBOMs and GitHub Attestations (in-toto compatible).

To verify the release artifacts:

```bash
# Verify the GitHub attestation
gh attestation verify dist/release/riopa-example-research-object.tar.gz --repo edithatogo/riopa-infrastructure

# Verify the SHA256 checksums
sha256sum --check SHA256SUMS
```

Negative tests should confirm that modified or unsigned artifacts fail these checks.
