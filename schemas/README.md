# Schemas

All schemas use JSON Schema Draft 2020-12. Versioned `$id` values are stable profile identifiers; repository paths are implementation locations.

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

## Integrity model

Schema validation is necessary but not sufficient. `riopa validate` also checks that:

- every manifest-local reference exists and remains inside the research-object root;
- the canonical manifest digest is correct;
- event sequence, stream identity, predecessor hashes and event hashes form a valid chain;
- sources, artifacts, transformation inputs/outputs and materialisations resolve to declared identifiers;
- rights, quality and methods records target the same snapshot;
- manifest capture identifiers have corresponding capture events.

Artifact records distinguish payload availability from verification. Synthetic fixtures therefore declare `payload_status: not-bundled` and `verification_status: synthetic-placeholder` rather than appearing to contain verified data.

## Stability

`1.0.0` in this scaffold is a candidate contract, not a declared stable public release. The first implementation track must validate it against at least `fyi-cli`, `fyi-archive`, one spatial connector and one NLP transformation before tagging v1.
