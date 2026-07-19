# Test and validation strategy

## Test pyramid

1. Schema and ontology examples, negative fixtures and migration fixtures.
2. Unit tests for hashing, identity, validation, queries, algorithms and packaging.
3. Property/metamorphic tests for transformations, canonicalisation, geometry and optimisation invariants.
4. Contract tests for connectors, source capabilities and repository adapters.
5. Cross-language golden conformance.
6. End-to-end real vertical slices.
7. Performance, load, fault-injection and recovery tests.
8. Independent clean-room reproduction and external-user journeys.

## Release-critical testing

- mutation or intentionally corrupted fixture tests for validators and solution verification;
- path traversal, malformed payload, decompression bomb and resource-limit tests;
- deterministic/tolerance-equivalent rebuild comparison;
- API/schema/ontology compatibility diff;
- security, dependency and SBOM verification;
- backup restore, source disappearance, rights change and withdrawal drills;
- spatial/temporal quality and causal/analytical sensitivity tests.

Coverage percentage is retained as a floor, not used as proof of maturity.
