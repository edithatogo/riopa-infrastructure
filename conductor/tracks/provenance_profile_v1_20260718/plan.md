# Plan: provenance_profile_v1_20260718

## 1. Evidence inventory

- [ ] 1.1 Map fyi-cli hash-chain fields and fyi-archive release provenance.
- [ ] 1.2 Map nlp-policy-nz and healthpoint-rs manifests/provenance.
- [ ] 1.3 Record gaps, collisions and source-specific extensions.

## 2. Contract stabilisation

- [ ] 2.1 Refine JSON Schemas and canonicalisation algorithm.
- [ ] 2.2 Define event-stream partitioning, ordering and retry semantics.
- [ ] 2.3 Define PROV/OpenLineage adapters and conformance fixtures.

## 3. Cross-language implementations

- [ ] 3.1 Implement reference Python library and CLI.
- [ ] 3.2 Implement Rust structs/validator or generate them from schema.
- [ ] 3.3 Run round-trip and semantic-equivalence tests.

## 4. Release

- [ ] 4.1 Publish candidate, solicit review and resolve issues.
- [ ] 4.2 Publish v1 with migration guide, examples and DOI.
- [ ] 4.3 Register stable w3id identifiers or equivalent redirects.
