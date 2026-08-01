# WP-010 external reproduction report template

Copy this template into the external operator's report. Do not include
secrets, private credentials or sensitive local paths.

## Identity and independence

- Reviewer/operator:
- Organisation:
- Relationship to the implementer:
- Conflicts disclosed:
- Signature, platform attestation or content-bound report URL:

## Environment

- Operating system and version:
- Architecture:
- Python version:
- UTC start time:
- UTC completion time:

## Frozen inputs

- Repository URL: `https://github.com/edithatogo/riopa-infrastructure`
- Exact commit: `6b99b3ee42110733b36fd7777c960832719359b8`
- Benchmark ID: `urn:riopa:benchmark:wp010:synthetic-methods:1.0.0`
- Reviewer-bundle SHA-256: `26bf2281f67c35f3327ebadeda3c8d5e7c6460e5b447dfc8417c851bcb0b6813`

## Commands and results

| Command | Exit status | stdout/stderr digest | Notes/deviations |
|---|---:|---|---|
| `git status --porcelain` |  |  |  |
| bundle build A |  |  |  |
| bundle build B |  |  |  |
| `cmp` of A and B |  |  |  |
| `python verify.py` |  |  |  |

## Findings and decision

- Findings:
- Unexpected dependencies or deviations:
- Decision: `pass` / `pass-with-limitations` / `fail`
- Scope limitation: this covers only the fixed synthetic calculation and
  deterministic handoff; it does not establish empirical calibration,
  operational fitness, national completeness or stable-v1 readiness.

Publish the completed report as an immutable or content-addressed artifact and
link it from issue [#149](https://github.com/edithatogo/riopa-infrastructure/issues/149).
