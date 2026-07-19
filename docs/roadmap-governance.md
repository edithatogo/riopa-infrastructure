# Roadmap and Conductor governance

## Sources of truth

- `conductor/tracks/*/spec.md` defines track acceptance.
- `conductor/tracks/*/plan.md` defines phased implementation.
- `conductor/tracks/*/metadata.json` defines state, dependencies and target release.
- `conductor/releases.json` defines release gates.
- `conductor/release-evidence/*.json` records gate outcomes.
- `project/issues.yaml` is generated from tracks and must not be hand-edited.

## Status transitions

`proposed → specified → ready → active → validating → complete → archived`

A track cannot become ready until acceptance is testable, active without an owner, validating without implementation evidence, or complete without linked evidence and completed dependencies.

## Drift control

`riopa roadmap validate` rejects unknown dependencies, cycles, missing files, invalid metadata, release omissions and generated issue drift. `riopa roadmap generate-issues` regenerates GitHub issue configuration from Conductor.

## Exceptions

Exceptions are evidence records, not prose comments. They identify scope, gate, approver, rationale, compensating control, expiry and remediation issue.


## Maturity and release closure

Track status and maturity are related but not interchangeable. `complete` means the track has reached its declared maturity target with linked evidence; a release may require an intermediate maturity from a track that remains active toward M6. Release readiness is computed from the exact required-track maturity, gate evidence, defect state, waiver validity and release-specific authority. A generated issue being closed is never sufficient evidence by itself.

The 0.2.0 roadmap release is the only currently ready release. It proves that the v1 scope and execution model are coherent at M1; it does not grant maturity to any planned platform capability.
