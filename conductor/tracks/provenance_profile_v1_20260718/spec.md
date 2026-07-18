# Track: Shared provenance, transformation and quality profile v1

Track ID: `provenance_profile_v1_20260718`  
Phase: **Core**

## Goal

Stabilise a cross-language profile that unifies semantic lineage, operational run evidence, integrity, rights and quality without replacing existing repository evidence.

## Dependencies

- `foundation_architecture_20260718`

## Scope

- Source, artifact, event, transformation, snapshot, materialisation and quality schemas.
- Canonical hashing and event-chain rules.
- W3C PROV and OpenLineage mappings.
- Granularity policy and bitemporal assertions.
- Compatibility adapters for existing fyi and NLP/health connector evidence.

## Out of scope

- A production graph database.
- Mandatory feature-level lineage for every dataset.

## Acceptance criteria

- [ ] Schemas validate examples and golden fixtures in Python and at least one non-Python implementation.
- [ ] Mappings identify exact, approximate and unmapped semantics.
- [ ] An fyi capture and an NLP transformation can be represented without losing existing evidence.
- [ ] Hash-chain tampering and manifest-parent omissions fail validation.
- [ ] Profile v1 migration and version policy are documented.

## Risks

- Overly broad schema.
- False precision at row/feature level.
- Duplicating OpenLineage or PROV concepts inconsistently.
