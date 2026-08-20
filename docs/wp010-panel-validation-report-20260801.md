# WP-010 panel validation report

**Status:** accepted for the bounded public-datasets-only technical preview.  
**Decision:** `pass-with-limitations`  
**Authority:** programme-owner-authorised three-agent subagent panel.  
**Scope:** regional, research-only, non-authoritative and non-operational.

## Frozen evidence

- Repository revision: `8cac8b019cd20f7ba276147567442003489ac5b5`
- Zenodo successor: [10.5281/zenodo.21737563](https://doi.org/10.5281/zenodo.21737563)
- Preserved packet SHA-256: `e0dcf5eb08e9b4530929da92a439d2cb97ced51bfe34f4848d1a2ef94c15abe5`
- Reviewer-bundle SHA-256: `26bf2281f67c35f3327ebadeda3c8d5e7c6460e5b447dfc8417c851bcb0b6813`

## Panel outputs

1. Reproducer: two clean-room bundle builds were byte-identical and matched the
   expected digest.
2. Adversarial analyst: no deviation was observed in the scripted synthetic
   benchmark; the report retains the declared limitations.
3. Evidence/rights auditor: preservation, source exclusions and public-only
   scope were consistent; no restricted or unpublished payload was introduced.

The orchestrator records concordance across these outputs. No dissent was
reported. The underlying preflight is documented in
`docs/wp010-internal-reproduction-preflight-20260801.md`.

## Limitations and gates retained

This report does not establish clinical fitness, dispatch suitability, national
completeness, causal validity, operational safety or external-human evidence.
The external operator requirements for beta, release candidate and stable-v1,
plus the global external workflow and release-authority thresholds, remain
unchanged and open.

Review this decision by **2026-08-31**, or sooner if scope, source status,
rights or safety changes. Any expansion reopens the relevant gates.
