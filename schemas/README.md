# Schemas

All schemas use JSON Schema Draft 2020-12. Versioned `$id` values are stable profile
identifiers; repository paths are implementation locations.

## Research-data and provenance contracts

| Schema | Purpose |
|---|---|
| `source-record` | publisher, access, rights and source metadata |
| `artifact` | content-addressed object identity, payload availability and verification state |
| `provenance-event` | append-only, hash-linked event backbone |
| `transformation-run` | detailed executable run record |
| `snapshot-manifest` | immutable release composition, reference closure and canonical digest |
| `materialization` | physical representation, fidelity and reproducibility class |
| `quality-report` | metric-level quality evidence and waivers |
| `rights-inventory` | source-level licensing, governance review and publication decision |
| `methods-facts` | structured facts used to generate publication methods and limitations |
| `spatial-feature-link` | evidence-based link between a spatial feature and plan provisions |

## Programme, maturity and release contracts

| Schema | Purpose |
|---|---|
| `track-metadata` | Conductor state, dependencies, maturity, ownership, risk and evidence |
| `maturity-model` | ordered M0–M6 levels and the 12 v1 maturity dimensions |
| `release-roadmap` | release train, required tracks and blocking exit gates |
| `release-evidence` | reviewed gate evidence, defects, metrics, approvals and artifacts |
| `v1-gate` | non-negotiable stable-v1 thresholds and post-release obligations |

## Integrity model

Schema validation is necessary but not sufficient. `riopa validate` also checks that:

- every manifest-local reference exists and remains inside the research-object root;
- the canonical manifest digest is correct;
- event sequence, stream identity, predecessor hashes and event hashes form a valid chain;
- sources, artifacts, transformation inputs/outputs and materialisations resolve to declared identifiers;
- rights, quality and methods records target the same snapshot; and
- manifest capture identifiers have corresponding capture events.

`riopa roadmap validate` additionally checks schema conformance, M0–M6 and semantic
release order, dependency closure, track/document drift, stable-v1 scope, gate/dimension
coverage, release-evidence references and digests, waiver validity and deterministic
issue generation.

Artifact records distinguish payload availability from verification. Synthetic fixtures
therefore declare `payload_status: not-bundled` and
`verification_status: synthetic-placeholder` rather than appearing to contain verified
data.

## Stability

`1.0.0` in the research-data schemas is a candidate profile version inside this
roadmap bundle, not a claim that the programme has reached stable GA. Normative v1
contracts must pass real connector/archive integrations, cross-language conformance,
migrations, independent review and the global stable gate before being frozen.
