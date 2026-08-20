# Solo-maintainer security context

RIOPA is operated as a single-developer repository. Pull requests require the
protected automated checks, but no second-person approval, CODEOWNERS rule,
team gate or human review is required. Repository assessment may use the
orchestrated agent panel described in
[`single-developer-agent-panel-review-policy.md`](single-developer-agent-panel-review-policy.md).

The `main` protection contract is fail-closed: force-push and branch deletion
are disabled; linear history, conversation resolution, strict status checks and
administrator enforcement are enabled. The live rule is verified with:

```sh
uv run python scripts/verify_github_main_protection.py
```

The required automated checks are `Quality, contracts, and packaging`, `Tests
on Python 3.14`, and `Analyze Python`. CodeQL and dependency review remain
additional hosted checks where GitHub supplies them.

Renovate app access, Codecov activation/OIDC receipts and provider-side secret
scanning are external platform gates. Repository configuration records them as
pending and never treats local configuration as proof of hosted activation.
Contribution, security disclosure, rights and release-scope boundaries are
canonicalised in `CONTRIBUTING.md`, `SECURITY.md`, the pull-request template
and the release evidence policy.
