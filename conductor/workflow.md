# Conductor workflow — stable v1 programme

## Track lifecycle

`proposed → specified → ready → active → validating → complete → archived`

Each track lives at `conductor/tracks/<track_id>/` and contains:

- `spec.md`: goal, v1 role, requirements, acceptance, maturity gates and evidence contract;
- `plan.md`: numbered implementation phases and closeout tasks;
- `metadata.json`: status, dependencies, target release, maturity, risk, priority and ownership;
- `index.md`: implementation evidence, decisions, exceptions and handover notes.

## Status transition gates

### Proposed → specified

- Problem, users, scope and non-goals are explicit.
- Dependencies and risks are visible.
- V1 role and target release are identified.

### Specified → ready

- Every acceptance criterion is testable.
- An owner repository and accountable person/role are assigned.
- Rights, security, governance and data requirements are understood.
- Required fixtures, source access and environments are available or explicitly staged.

### Ready → active

- Blocking dependencies required for the first phase are complete or a safe parallel interface is frozen.
- GitHub parent/sub-issues exist and Project fields are synchronised.
- The first implementation slice and evidence plan are agreed.

### Active → validating

- Planned implementation is code-complete for the target release.
- Tests, migrations, documentation and release artifacts exist.
- Evidence paths are linked in `index.md`.

### Validating → complete

- All acceptance criteria pass.
- Blocking dependencies are complete.
- Security, rights/governance, compatibility and operational reviews pass.
- Independent review/reproduction requirements are satisfied.
- No expired waiver or undocumented limitation remains.

## Release lifecycle

`architecture → alpha → beta → release candidate → stable`

Track completion does not make a release ready. `conductor/releases.json` defines cross-track blocking gates and `conductor/release-evidence/<version>.json` records results.

A release may advance only when:

1. `riopa roadmap validate` passes;
2. required tracks are complete;
3. every blocking release gate is passed or has a valid approved waiver;
4. signed artifacts, checksums and release evidence agree;
5. the release authority records the decision.

## GitHub mapping

- One programme epic represents stable v1 delivery.
- Every Conductor track maps to one parent issue.
- Every numbered plan phase maps to a sequential sub-issue.
- Parent dependency links mirror `depends_on` metadata.
- Phase sub-issues are blocked by the preceding phase.
- Cross-repository work is created in the owning repository.
- Selected parent issues may be mirrored to the RIOPA umbrella project.
- `project/issues.yaml` is generated and must not be hand edited.

## Implementation rules

1. Raw/source evidence is immutable; corrections create successor evidence.
2. Normative schema changes require positive/negative fixtures, migrations and compatibility classification.
3. Connector work requires rights/access review, load policy, offline fixtures and source-health handling.
4. Analytical work requires formula/model specifications, independent verification and explicit uncertainty/equity choices.
5. AI-assisted work records model/tool identity, inputs/outputs or hashes, parameters, reviewer and decision without exposing restricted content.
6. Releases require quality, rights, citation, methods, SBOM, attestations, preservation and clean-build evidence appropriate to the maturity level.
7. Waivers are scoped, approved, time limited and machine readable.

## Pull-request gates

- schema, ontology and roadmap validation;
- generated issue-graph drift check;
- unit, integration, contract, negative and compatibility tests;
- linting, formatting, type/static analysis and dependency review;
- licence, attribution, privacy, governance and threat-review triggers;
- deterministic or tolerance-equivalent rebuild tests where affected;
- documentation, migration and changelog updates;
- performance regression checks for release-critical paths.

## Programme review cadence

### Continuous

- CI gates and source/operation alerts.
- Security and rights changes can immediately block release/publication.

### Monthly

- Track status, blockers, evidence and waiver expiry.
- Source freshness, connector health, quality regressions and costs.
- Adoption, compatibility and unresolved semantic mappings.

### At every release candidate

- Feature/normative inventory and API/schema/ontology diff.
- Security, performance, documentation and governance audit.
- Migration, rollback, restore, correction and withdrawal rehearsal.
- Clean-room reproduction and external-user validation.
