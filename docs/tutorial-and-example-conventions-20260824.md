# Tutorial and example conventions

Tutorials are executable documentation, not evidence of production readiness.

## Required properties

- Pin Python to 3.14 and use the locked `uv` environment.
- Use public or synthetic fixtures only; never embed credentials, private data,
  live GIS payloads or machine-local paths.
- Prefer offline, deterministic fixtures. A tutorial that contacts a live
  endpoint must be separately labelled as an acquisition exercise and must not
  be used as source truth without a content-addressed capture.
- Include one positive path, one malformed-input or rights/integrity failure,
  and the expected fail-closed result.
- Show the exact command, expected artifact paths and validation command.
- Distinguish local validation, hosted CI, merged code, publication receipts
  and release-authority decisions.
- Record the revision and fixture digest when a result is reproducibility
  relevant.

## Status labels

Use `example`, `bounded-rehearsal`, `hosted-observation`, `published`, or
`release-evidence`. Do not call a fixture, agent-panel report or retrospective
measurement an external reproduction, operational qualification or authority
decision.

## Accessibility and safety

Use descriptive headings, text alternatives for diagrams, copyable commands,
visible failure messages and terminology consistent with the schemas. Keep the
bounded public, non-operational technical-preview scope visible at the point of
use.
