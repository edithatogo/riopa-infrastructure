# Foundation M2 evidence checklist

This checklist defines the smallest repository-owned evidence slice for moving
the foundation track from M1 toward M2. It is a qualification checklist, not
release approval.

| M2 requirement | Executable evidence | Pass condition | Current state |
|---|---|---|---|
| Architecture boundary proof | `uv run riopa roadmap validate`; `tests/test_roadmap_hardening.py::test_architecture_fitness_requires_boundary_contract` | Validator passes and the negative test rejects a missing boundary contract | Passed locally on the current main revision |
| Dependency and issue-graph proof | `uv run riopa roadmap generate-issues && uv run riopa roadmap validate` | Generated issue graph is deterministic and digest-checked | Passed locally; hosted exact-head confirmation remains separate |
| Contract ownership proof | `docs/contract-ownership-matrix.md` and `tests/test_roadmap_hardening.py` | Every normative boundary has an owner, compatibility policy and migration path | Recorded for M1; representative real-data migration remains open for M3 |
| Decision traceability | `docs/architecture-baseline-ratification.md`, ADR register and closeout audit | Decisions are accepted, deferred or scoped with owner and revisit date | Passed for M1; stable authority remains open |

M2 exit requires a fresh revision-addressed validation report and negative-test
results. M2 does not authorize real-data acquisition, operational use, beta,
release-candidate or stable-v1 publication.
