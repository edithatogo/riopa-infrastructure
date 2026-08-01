# Branch Protection and CI Policy

## Branch Protection
- **`main` and release branches:** Direct pushes are disabled.
- **Reviews:** All changes require at least one approved code review from a designated maintainer.
- **Status Checks:** CI checks (linting, tests, security audits) must pass before merging.

## Least-Privilege Workflow Permissions
- GitHub Actions workflows use `permissions: read-all` by default.
- Write access to repositories, packages, or attestations is granted only to specific, protected release jobs.

## CI Hardening
- Dependency review and static analysis are enforced on all pull requests.
- Secret scanning is enabled for the repository.
- Actions and container images used in workflows must be pinned to immutable SHAs.
