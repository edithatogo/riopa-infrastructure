# Hosted quality-gate blocker register

This register separates repository-owned checks from GitHub-hosted settings
that cannot be changed by a local commit. It is intentionally non-assertive:
an issue remains open until the hosted observation or configuration receipt is
attached.

| Blocker | Repository preparation | Hosted action required | Evidence of closure | Fallback |
| --- | --- | --- | --- | --- |
| Branch protection/ruleset | Workflows expose stable quality and security jobs; PR template requires the local gate. | Configure a ruleset against `main` blocking force-push/deletion and requiring the stable checks, while retaining zero mandatory human approvals. | Exported ruleset/settings receipt and a protected-branch test PR. | Keep merge/release authority manual and do not claim protected-branch qualification. |
| Renovate ownership | `.github/dependabot.yml` remains visible; dependency policy is documented. | Grant Renovate access, verify the inherited configuration and Dependency Dashboard/first PR, then remove Dependabot only after continuity is proven. | Renovate dashboard or PR URL plus configuration snapshot. | Leave Dependabot in place and record Renovate as deferred; do not run competing bots. |
| Codecov/OIDC | CI uploads coverage artifacts and uses least-privilege workflow permissions. | Enable Codecov repository integration and verify OIDC/status reporting on the current head. | Codecov project/status URL and commit receipt. | Treat local coverage as evidence only; do not claim hosted coverage qualification. |
| Hosted CI exact-head checks | Local tests, roadmap validation and reproducibility scripts pass. | Confirm required checks completed on the exact protected head after any rebase or merge-queue operation. | GitHub check-run URLs for the exact commit. | Keep the change unmerged or re-run checks; never infer from stale/local green status. |

## Operating rule

Only the repository owner or an authorised GitHub administrator can close the
hosted rows. Agents may prepare configuration, inspect public status and draft
receipts, but must not represent a local commit as proof that a hosted setting
is active.

The hosted rows are independent of the elapsed beta/RC soak, production
restore/rollback, national-scale measurement, panel qualification and release
authority gates. Closing one does not promote the release tier.

