# Security Threat and Trust Model

## Assets
- Code repositories and branches
- CI/CD pipelines and secrets
- Release artifacts (binaries, containers, research objects)
- Published data and provenance records

## Actors
- Contributors (untrusted pull requests)
- Maintainers (trusted reviewers and approvers)
- Build systems (automated runners)
- Consumers (end-users of releases)

## Trust Boundaries
- Pull requests from forks vs internal branches
- CI environments (build vs release)
- External dependencies and actions

## Abuse Cases
- Source spoofing or unauthorized code changes
- Dependency compromise (supply-chain attack)
- Credential theft and misuse
- Malicious data injection
- Publication tampering
- Denial of service against infrastructure

## Credentials and Environments
- **Production Credentials:** Strictly isolated to release environments; never exposed to PR builds.
- **Release Authorities:** Designated maintainers with multi-factor authentication and protected branch access.

## Severity and Release-Blocking Rules
- **Critical/High Findings:** Must be mitigated or have an approved, time-limited exception before any stable release.
- **Blocking Policy:** Any unresolved critical vulnerability blocks the release pipeline.
