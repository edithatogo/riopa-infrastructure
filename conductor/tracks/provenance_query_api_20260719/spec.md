# Track: Queryable provenance and impact-analysis API

Track ID: `provenance_query_api_20260719`  
Phase: **Core**  
Target release: **0.6.0**  
Maturity target: **M6**  
Stability class: **Platform**  
V1 critical: **yes**

## Goal

Expose reliable answers to where, why and how lineage questions through CLI, Python, relational, graph and MCP interfaces without making a graph database authoritative.

## v1 role

This track is part of the stable v1 release contract. It is complete only when its implementation, compatibility, quality, security/governance, operational and reproducibility evidence satisfy both this specification and every applicable blocking gate in `conductor/releases.json` and `conductor/v1-gate.json`.

## Dependencies


- `canonical_domain_schemas_ontology_20260719`
- `provenance_profile_v1_20260718`

## Scope

- Artifact, dataset, partition, feature and row lineage query contracts.
- Source-to-output, output-to-source, downstream impact and rebuild-scope queries.
- Deterministic relational and optional graph projections from authoritative events/manifests.
- CLI, Python API, MCP server and query examples.
- Query performance, caching, access control and explicit granularity limitations.

## Out of scope

- Making a graph store the source of truth.
- Fabricating feature or row lineage from dataset-level evidence.

## Requirements

- **R01.** Every query response states lineage granularity, evidence IDs and projection freshness.
- **R02.** The same authoritative event/manifest set produces equivalent relational and graph answers.
- **R03.** Impact analysis is conservative when dependencies are incomplete.
- **R04.** Restricted lineage is filtered without pretending the hidden evidence does not exist.
- **R05.** Projection rebuilds are deterministic and tested after schema migrations.

## Acceptance criteria

- [ ] Users can query source, transformation, methods, downstream dependency, supersession and rebuild impact for a real release.
- [ ] CLI, Python and MCP interfaces pass one shared conformance corpus.
- [ ] Dataset/partition lineage is mandatory and feature/row granularity is reported only when captured.
- [ ] Relational and graph projections return equivalent answers for normative queries.
- [ ] Representative lineage queries meet documented performance budgets.
- [ ] A projection can be deleted and rebuilt without loss from authoritative evidence.

## Hardening and maturity gates

- M2 requires executable proof, negative tests and traceable evidence; interfaces may remain experimental.
- M3 requires real-data integration, migration evidence and representative failure handling.
- M4 requires repeated operation, representative agent-operated use, SLO evidence and bounded compatibility changes.
- M5 requires frozen interfaces, orchestrated agent-panel qualification, security/performance/recovery qualification and release-candidate soak.
- M6 requires supported compatibility, signed and preserved releases, isolated role-separated clean-room agent reproduction, named maintainers and post-release verification.
- Exceptions must be machine-readable, scoped, approved, time-limited and visible in release evidence.

## Evidence required

- Normative query specification and conformance corpus.
- CLI/Python/MCP integration tests.
- Relational/graph equivalence and rebuild reports.
- Performance, access-control and granularity reports.

## Risks

- Graph-specific semantics leak into the core contract.
- Impact analysis misses undeclared side inputs.
- Lineage volume makes interactive queries unusable.
- Restricted evidence is exposed through traversal.

## Completion rule

The track may enter `complete` only after every acceptance criterion is evidenced in `index.md`, all blocking dependencies are complete, required migrations and documentation are published, and the target release readiness evaluator reports no track-specific blocker.
