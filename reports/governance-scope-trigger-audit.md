# Scope-triggered governance audit

- **Date:** 2026-08-01
- **Evidence:** `e80b274`
- **Command:** `uv run pytest tests/test_governance.py -q`
- **Result:** 14 tests passed

## Boundary verified

Review domains are derived only from explicitly declared scope labels through
`scope_review_triggers`. Place names, population labels and inferred identity
do not activate a cultural or community review. The helper is deterministic,
deduplicates domains, and rejects a scalar scope value. This preserves a
fail-closed pathway when a review is explicitly required without introducing a
mandatory Māori governance or co-design gate.

## Remaining evidence

This is repository-level contract evidence only. Any concrete dataset or pilot
still requires its own rights, privacy, safety and benefit/harm decision. No
live community engagement, legal certification or operational takedown is
claimed by this audit.
