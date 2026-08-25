# Planning linkage methods and limitations (bounded candidate)

This document freezes the repository-owned, reference-only method for carrying
planning links. It is a versioned documentation candidate, not a planning
authority determination.

## Method sequence

1. Preserve a declared plan/version, source locator, document digest and
   structure digest with `build_plan_source_intake`.
2. Record provision extraction method, input/text digests, uncertainty and
   tool identity with `build_provision_extraction_record`.
3. Preserve feature-to-provision references with
   `build_feature_provision_linkage`; duplicate evidence is normalised but no
   legal effect is inferred.
4. Preserve hierarchy, exceptions, combined rules and unresolved reasons with
   `build_rule_structure_record`.
5. Map source labels to canonical concepts with
   `build_planning_concept_crosswalk`, retaining source assertions and review
   state.
6. Answer bounded feasibility queries with
   `build_planning_feasibility_record`; conflicting or unresolved rules remain
   unresolved and require authority outside this repository.

All records are digest-bound where applicable, deterministic, and promotion
disabled. The two-structure synthetic validation is recorded in
`docs/planning-two-structure-validation-20260825.json`.

## Non-authority limitations

- These records do not establish operative legal status, consent, zoning advice,
  completeness, or council authority.
- A source locator or matching digest is not proof that source bytes are
  preserved, current, licensed, or legally effective.
- Synthetic structure variation is not real council coverage and cannot replace
  factual source capture or a panel-of-agents sample review.
- External participant evidence, preservation acceptance, national coverage and
  accountable release authority remain open.
