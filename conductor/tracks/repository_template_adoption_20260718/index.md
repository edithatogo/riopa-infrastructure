# Evidence index: Repository template and cross-repository adoption

- **Track ID:** `repository_template_adoption_20260718`
- **Status:** `specified`
- **Target release:** `0.5.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Platform`
- **Risk / priority:** `High` / `P1`
- **V1 critical:** `yes`
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Core platform maintainer
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/44

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| `WP-008-related-repository-adapters-20260731` | Related repositories have isolated issue, branch, tested commit and pull-request implementations without modifying dirty checkouts | `reports/wp008-cross-repository-adapters.md`, `conformance/adapters/report.json` | Local implementation and cross-repository fixture validation pass; PRs are open and unmerged pending exact-head hosted checks |

## Blocking defects

- Related-repository PRs #285 (`fyi-cli`) and #319 (`fyi-archive`) remain
  unmerged pending their exact-head hosted checks.

## Decisions, exceptions and limitations

- This evidence is bounded to the two adapter contracts and does not establish
  template adoption or release conformance for either complete repository.

## Review and handover

Required reviewer roles: API/schema reviewer, Security reviewer, Research-object reviewer, External user reviewer.

This index is deliberately non-assertive while the track remains `specified`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, independently reviewed where required, and sufficient for the applicable release gates.
