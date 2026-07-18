# Track: Repository template and cross-repository adoption

Track ID: `repository_template_adoption_20260718`  
Phase: **Core**

## Goal

Make provenance-first setup and staged adoption easy across existing and future repositories without destructive rewrites.

## Dependencies

- `provenance_profile_v1_20260718`
- `methods_research_objects_20260718`

## Scope

- Conductor-aware repository template.
- GitHub repository/project/issue bootstrap.
- Language-specific adapter templates.
- Adoption matrix and compatibility tests.
- Initial adoption in fyi-cli, fyi-archive, nlp-policy-nz and healthpoint-rs.

## Out of scope

- Forcing all repositories into Python.
- Replacing source-specific manifests before dual-run validation.

## Acceptance criteria

- [ ] One command creates a repository, project, labels, track issues and dependencies.
- [ ] Template validation passes in a fresh checkout.
- [ ] At least three existing repositories reach adoption level A1 and one reaches A3.
- [ ] Existing outputs continue during a documented dual-run period.
- [ ] Cross-repo compatibility is tested against pinned fixtures.

## Risks

- Template coupling to current GitHub CLI.
- Excessive boilerplate.
- Breaking mature repository-specific workflows.
