# Provenance profile mapping inventory

This inventory records the repository-owned mapping baseline for
`provenance_profile_v1_20260718`. It does not claim cross-repository authority
or external conformance.

| Native evidence family | Profile treatment | Classification |
| --- | --- | --- |
| Capture/archive receipts | Source, capture, artifact and snapshot events with content hashes | exact or extension-preserved |
| Corpus and policy records | Source assertions, rights, quality and governance facets | exact where fields exist; unmapped fields are retained in extensions |
| Research-object outputs | Transformation, materialisation, methods and publication projections | extension-preserved with parent identities |
| Health/analytical evidence | Analysis and quality records with uncertainty and limitation fields | approximate where source semantics differ; no causal claim inferred |

## Profile boundaries

- Canonical JSON uses the named RFC 8785-compatible hashing helper and golden
  fixtures.
- Stream/partition sequence, causal parents, retries, checkpoints and
  idempotency are validated by the event and pipeline suites.
- PROV JSON-LD and OpenLineage projections are emitted by the research-object
  builder; signed attestation output remains a release-tier gate.
- Manual, adjudication and AI-assistance facets retain reviewer, tool/model,
  parameters, inputs, outputs and decision fields without exposing restricted
  payloads.

## Unresolved gates

Non-Python acceptance/rejection parity, independent projection round trips,
profile publication, signed v1 attestation and independent review remain
pending. Native evidence is not rewritten destructively.

