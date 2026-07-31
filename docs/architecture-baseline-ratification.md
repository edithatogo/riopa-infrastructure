# Development architecture baseline ratification

## Decision

The programme owner ratifies the architecture recorded at source revision
`64c4dd7c28d18f1ed68f28a52421770777f92d7d` as the RIOPA development-stage
M1 baseline. The authorization reference is the 2026-08-01 Codex task
instruction to proceed with the recommended bounded M1 ratification.

This decision accepts the documented product boundary, federated responsibility
model, independent version axes, compatibility policy, decision rights,
development release train and machine-checkable programme governance as the
baseline against which later implementation and migration are reviewed.

## Scope and non-approval boundary

This is an architecture-baseline decision, not a software, dataset, model,
research-object, release-candidate or stable-v1 approval. In particular, it:

- does not change any track's current M1 maturity or claim M2-M6 evidence;
- does not approve the 0.3.0 alpha, 0.9.0 release candidate or 1.0.0 stable
  release;
- does not satisfy named signatory, signed-attestation, security qualification,
  operational soak, preservation or external reproduction gates;
- does not convert deferred ADR-0006, ADR-0009 or ADR-0011 into accepted
  decisions; and
- does not authorize publication, deployment, live data acquisition or an
  operational, legal, clinical or commercial claim.

The 0.2.0 development roadmap is ready at M1. The 0.3.0 release remains not
ready because its required tracks remain below M2 and its four blocking gates
remain unpassed. Stable v1 remains governed by `docs/v1-release-policy.md`,
`conductor/v1-gate.json` and a separate signed release-authority decision.

## Evidence and finding disposition

- The architecture and governance analyst records are attributed and have
  distinct scopes.
- Deferred ADRs have named owners, revisit dates and follow-up tracks in
  `docs/adr/README.md`.
- Normative contracts have owners, compatibility rules and migration checks in
  `docs/contract-ownership-matrix.md`.
- The locked Python 3.12/3.13 suite, unchanged 90% branch-coverage gate,
  roadmap validation, issue regeneration, quality, packaging and
  reproducibility checks pass; exact-head hosted CI and CodeQL passed for
  revision `64c4dd7c28d18f1ed68f28a52421770777f92d7d`.
- Generated issue wording permits two independent analysts, including agents,
  rather than requiring two separate human maintainers.

The analyst findings are therefore resolved for this bounded M1 ratification
or explicitly deferred to their named later gates. Named stable-release
signatories and external review remain deliberately outstanding.

## Lifecycle consequence

Plan task 4.3 is complete. The foundation track remains `active` at M1 because
its M6 completion rule and closeout gates are not satisfied. Ratifying this
baseline must not be represented as track completion or archival eligibility.
