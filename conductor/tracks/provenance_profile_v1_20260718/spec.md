# Track: Shared provenance, transformation and quality profile v1

Track ID: `provenance_profile_v1_20260718`  
Phase: **Core**  
Target release: **0.3.0**  
Maturity target: **M6**  
Stability class: **Normative**  
V1 critical: **yes**

## Goal

Stabilise a cross-language profile that unifies capture, transformation, lineage, manual and AI assistance, integrity, rights and quality without replacing repository-native evidence.

## v1 role

This track is part of the stable v1 release contract. It is complete only when its implementation, compatibility, quality, security/governance, operational and reproducibility evidence satisfy both this specification and every applicable blocking gate in `conductor/releases.json` and `conductor/v1-gate.json`.

## Dependencies


- `foundation_architecture_20260718`
- `security_supply_chain_20260719`

## Scope

- Source, artifact, capture, event, transformation, snapshot, materialisation, rights and quality contracts.
- Named JSON canonicalisation, hashing, stream partition, retry, parent and checkpoint semantics.
- W3C PROV, OpenLineage and build-attestation projections.
- Manual intervention, adjudication and AI-assisted transformation evidence.
- Adapters for current fyi, archive, corpus, policy and health provenance.

## Out of scope

- Requiring a graph database for capture or transformation.
- Claiming deterministic AI reproducibility where the provider cannot support it.
- Mandatory row-level lineage where stable source identity is absent.

## Requirements

- **R01.** Every event has stream/partition identity, idempotency, causal parents and authenticated release context where applicable.
- **R02.** Canonical hashes use a named cross-language algorithm and published golden vectors.
- **R03.** Lineage granularity is declared and unsupported precision is rejected.
- **R04.** Manual and AI activity includes inputs, outputs, parameters, model/tool identity, reviewer and decision.
- **R05.** Existing native evidence is dual-emitted or referenced rather than destructively rewritten.

## Acceptance criteria

- [ ] Python and at least one non-Python implementation accept and reject identical golden fixtures.
- [ ] Mappings classify every existing field as exact, approximate, extension-preserved, conflicting or unmapped.
- [ ] Concurrent streams, retries, partial failures, checkpoints and late events pass conformance tests.
- [ ] Tampering, missing parents, invalid rights state, stale schema and false granularity claims fail validation.
- [ ] PROV, OpenLineage and attestation projections round-trip required semantics or document bounded loss.
- [ ] Profile v1 has a stable identifier, migration guide, deprecation policy and orchestrated agent-panel qualification.

## Hardening and maturity gates

- M2 requires executable proof, negative tests and traceable evidence; interfaces may remain experimental.
- M3 requires real-data integration, migration evidence and representative failure handling.
- M4 requires repeated operation, external use, SLO evidence and bounded compatibility changes.
- M5 requires frozen interfaces, orchestrated agent-panel qualification, security/performance/recovery qualification and release-candidate soak.
- M6 requires supported compatibility, signed and preserved releases, external reproduction, named maintainers and post-release verification.
- Exceptions must be machine-readable, scoped, approved, time-limited and visible in release evidence.

## Evidence required

- Normative schemas, canonicalisation vectors and event conformance suite.
- Repository mapping and semantic-loss reports.
- Cross-language validation and projection round-trip reports.
- Security/signature and tamper-negative fixtures.

## Risks

- A universal profile becomes too broad to implement reliably.
- One linear hash chain cannot scale to concurrent connectors.
- OpenLineage or PROV terms are used inconsistently.
- AI provenance records expose sensitive prompts or copyrighted payloads.

## Completion rule

The track may enter `complete` only after every acceptance criterion is evidenced in `index.md`, all blocking dependencies are complete, required migrations and documentation are published, and the target release readiness evaluator reports no track-specific blocker.
