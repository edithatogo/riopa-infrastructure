# Evidence index: Bounded v0.2.0 roadmap technical-preview release

- **Status:** `archived` / complete at `M1`
- **Target release:** `0.2.0`
- **Release:** https://github.com/edithatogo/riopa-infrastructure/releases/tag/v0.2.0
- **Historical source:** `4ffe73eb144c5c1a4acad34706a5f5937491d1ad`
- **Passed run:** https://github.com/edithatogo/riopa-infrastructure/actions/runs/32865862594
- **Support ends:** `2027-08-25T15:27:39Z`

## Evidence

| Contract | Evidence | Result |
|---|---|---|
| Exact identity | annotated tag object `c444e79397f2455071c2b930e56b7887c29e0c40` | Resolves to exact historical commit |
| Hosted validation and build | Actions run #32865862594 | Passed |
| Research-object asset | SHA-256 `9e71e585289e0480907f699daf94f425dcb38517b81babf0a52c80b938ee79d1` | Downloaded checksum passed |
| Checksum asset | SHA-256 `5e58dcd0e36aaad158b4e3560634b677ba43918037c60ef83247681ed8ffce9b` | Downloaded digest passed |
| Provenance | GitHub OIDC SLSA attestation with Rekor timestamp | Verified for both subjects |
| Decision and support | `docs/v0.2.0-technical-preview-release-decision-20260826.json`; `docs/v0.2.0-technical-preview-support-20260826.md` | Published and content-bound |
| Review | `docs/v0.2.0-technical-preview-closeout-20260826.json` | Four findings resolved; two limitations disclosed |
| External programme | issue #605 | Three roles recruited; zero completions claimed |

## Accepted limitations

- The annotated Git tag is not personally GPG/SSH-signed because no signing
  identity was configured. GitHub OIDC provenance covers the released assets.
- No Zenodo credential was available, so no DOI or preservation deposition is
  claimed. This remains later publication/preservation work.
- External participant evidence remains absent and is required by later gates.

## Later-track invariant

All 28 stable-v1 tracks remain open under their existing status, maturity,
target-release and acceptance contracts. This archive has no effect on them.
