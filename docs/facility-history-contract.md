# Facility history contract

`FacilityHistoryEvent` records opening, closure, relocation, rebrand and
source-disagreement observations without rewriting source assertions. Every
event has a valid-time start, a recorded-at date, source assertion identities
and human-readable details. A deterministic snapshot rejects duplicate event
identifiers and is explicitly non-authoritative.

The contract distinguishes when a change was effective from when the archive
learned it. It does not infer closure from source disappearance, resolve
conflicting assertions, or publish sensitive/restricted facility locations.
Those decisions remain separate governance and agent-panel gates.

Source assertions also carry one of the governance release classifications
`public`, `restricted`, `sensitive` or `controlled`. `public_release_snapshot`
emits only `public` assertions and records every excluded assertion ID. Raw
source packets remain untouched; filtering is a release projection, not data
deletion or a rights decision.
