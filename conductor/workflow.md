# Conductor Workflow

## Track lifecycle

`proposed → specified → ready → active → validating → complete → archived`

Each track lives at `conductor/tracks/<track_id>/` and contains:

- `spec.md`: problem, goals, scope, requirements, acceptance criteria and risks;
- `plan.md`: phased, checkable implementation tasks;
- `metadata.json`: machine-readable status, dependencies and ownership;
- `index.md`: current state, evidence links, decisions and handover notes.

## GitHub mapping

- One programme epic issue represents this repository.
- Every Conductor track maps to one parent issue.
- Plan tasks may map to sub-issues when independently deliverable.
- Explicit GitHub issue dependencies mirror `depends_on` metadata.
- Cross-repository adoption work is created in the owning repository and linked from the programme epic.
- Selected parent issues are mirrored to the existing RIOPA umbrella project; repository-native projects remain the source workflow surface.

## Implementation rules

1. A track cannot enter `ready` until acceptance criteria are testable.
2. A track cannot enter `complete` without evidence paths or links in `index.md`.
3. Schema changes require examples, migration notes, compatibility tests and a version decision.
4. Source connectors require an access/rights assessment and a synthetic or public fixture.
5. Releases require validation, checksums, provenance, quality report, SBOM, research-object metadata and generated methods.
6. Corrections produce a successor snapshot with a relationship to the superseded release.

## Pull-request gate

- Contract validation and example validation.
- Unit/integration tests and deterministic hash tests.
- Licence and attribution completeness.
- Threat/privacy/governance review where triggered.
- Documentation and migration notes.
- Rebuild evidence for publication changes.

## Monthly programme review

- Review source freshness and connector health.
- Review blocked tracks and cross-repo dependencies.
- Review schema adoption and compatibility.
- Review quality trends and unresolved rights fields.
- Publish a project status update with evidence counts.
