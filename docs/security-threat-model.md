# RIOPA security threat model (bounded M1)

| Asset | Threat | Boundary/control | Release consequence |
|---|---|---|---|
| Source and release manifests | spoofing or tampering | protected branches, reviewed commits, checksums and attestation verification | block release |
| CI credentials and tokens | pull-request exfiltration | read-only default permissions, environment-scoped release credentials, no secrets in fixtures | revoke, rotate and block release |
| Dependencies and actions | dependency or action compromise | lockfiles, dependency review, static/security scans and immutable action references where available | block affected release |
| Public source payloads | parser abuse, malicious content or resource exhaustion | bounded fetches, validation, provenance and fail-closed parsing | quarantine evidence and block publication |
| Published research objects | replacement or deletion | content hashes, signed manifests and preserved release evidence | withdraw affected artifact |
| Services and registries | denial of service or outage | bounded retries, offline fixtures, resumable state and documented fallback | defer operation; no fabricated evidence |

The model distinguishes authenticated authorship from accidental corruption. It
does not claim upstream services are trustworthy or that local checks replace
hosted protection, protected release environments or independent verification.
