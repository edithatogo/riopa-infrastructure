# Governance withdrawal and pathway drill

- **Date:** 2026-07-29
- **Command:** standalone import of `src/riopa_provenance/governance.py` with
  a bounded public decision, withdrawal successor and controlled decision
- **Result:** `PASS governance withdrawal/public-controlled drill`

Assertions covered:

- an allowed public decision permits its declared scope;
- a withdrawal successor retains the predecessor reference and blocks public
  evaluation;
- a controlled classification is rejected by the public pathway and accepted
  only by the controlled pathway.

This is a synthetic contract drill; it is not evidence of live takedown,
external distribution reconciliation or Māori governance approval.
