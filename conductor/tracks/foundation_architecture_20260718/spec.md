# Track: Foundation architecture and programme governance

Track ID: `foundation_architecture_20260718`  
Phase: **Foundation**

## Goal

Ratify the federated architecture, responsibility boundaries, version axes, governance model and implementation sequence.

## Dependencies

- None.

## Scope

- Review and accept/revise ADR-0001 through ADR-0007.
- Define repository/package extraction criteria and ownership boundaries.
- Establish programme, repository-project and RIOPA umbrella-project operating model.
- Freeze v0.1 terminology, identity patterns and release gates.

## Out of scope

- Implement production connectors or analytics.
- Create a central operational database.

## Acceptance criteria

- [ ] All ADRs have an explicit accepted/superseded decision and rationale.
- [ ] Architecture diagrams and component contracts pass stakeholder review.
- [ ] Every later track has an owner repository, dependencies and measurable acceptance evidence.
- [ ] Programme epic, track issues and project fields can be generated from versioned configuration.

## Risks

- Premature package splitting.
- Architecture becoming aspirational rather than executable.
