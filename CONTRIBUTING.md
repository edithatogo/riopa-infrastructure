# Contributing

1. Identify or create a Conductor track and GitHub issue.
2. State the contract, evidence and rights/governance impact before implementation.
3. Add or update JSON Schema, examples and compatibility tests for contract changes.
4. Preserve raw evidence and emit provenance for generated artifacts.
5. Use Conventional Commits and link the issue/track.
6. Do not commit credentials, restricted source payloads or genuine health unit records.

## Local quality gate

Before opening a pull request, run the same repository-owned checks used by the
handoff and evidence workflows:

```sh
uv run pytest -q
uv run riopa roadmap validate
git diff --check
```

Generated manifests and reports must be regenerated from their source inputs;
the committed readiness projection has a regression test to detect drift.

Automated agents may implement, reproduce and audit repository-owned evidence,
but they must label elapsed-time, external-operator, custodian and
release-authority evidence as pending until the required independent record
exists. A passing local test does not authorise a higher release tier.

A contribution that changes meaning must include migration guidance and an explicit schema/version decision.
