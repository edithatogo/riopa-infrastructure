# External dependency and release-gate register

This register separates repository-owned work from evidence that requires an
source custodian, preservation service or named release authority. There is no
external human operator in the single-person operating model; workflow evidence
is produced by owner-authorized agents and assessed by an agent panel.
It is a planning and handoff artifact, not an approval record.

The current recommended regional-first technical-preview posture is recorded in
`docs/wp010-release-posture.md`; unresolved approvals remain explicitly TBD.

| Gate | Current state | Closure evidence | Responsible party | Fallback and promotion consequence |
|---|---|---|---|---|
| Agent WP-010 reproduction | Bounded pilot review passed with limitations; hosted clean-room and two agent workflow reports now exist; issue [#149](https://github.com/edithatogo/riopa-infrastructure/issues/149) remains open for final disposition | Pilot/beta/stable: owner-authorized agent identity, environment, exact revision/bundle digest, commands, findings and content-bound report | Agent panel may assess the reports but may not approve promotion | Pilot may remain regional and non-operational; no higher-tier claim without elapsed evidence and the owner's tier decision |
| Ambulance source authority | **Non-public acquisition gate closed for current public-datasets-only scope**; public-source authority/licence questions remain open for any national, provider-authoritative, current-service or operational claim | For current scope: no non-public payload acquisition. For future expansion: public-source terms/authority receipt or custodian approval, exact source receipt and rights record | Programme owner for scope; source custodian for expansion | Pilot remains regional and non-operational; no national-completeness claim; reopen only on scope expansion |
| Supermarket source rights | Partially bounded | Licence/terms record for every source and derived-output decision | Data steward and source custodian | Retain only rights-cleared OSM/aggregate outputs; exclude uncertain sources |
| Evidence preservation | Closed for WP-010 pilot packet and successor | Original Zenodo DOI [`10.5281/zenodo.21735818`](https://doi.org/10.5281/zenodo.21735818); successor DOI [`10.5281/zenodo.21737563`](https://doi.org/10.5281/zenodo.21737563), record URL, deposited packet SHA-256 and decision record | Preservation repository and programme owner | This does not close beta/stable evidence gates |
| Release authority | Repository owner is the accountable authority; tier-specific decision remains to be recorded before promotion | Owner decision, scope, exclusions, expiry and rollback/revocation conditions for each promotion tier | Agent panel cannot approve on the owner's behalf | Retain technical-preview status until the owner's tier decision and all evidence gates are recorded |
| Hosted verification | Passed for `ff328458f61fe8a5448979fcea04e4dbfba72afc` | CI run [30682545412](https://github.com/edithatogo/riopa-infrastructure/actions/runs/30682545412) and CodeQL run [30682545414](https://github.com/edithatogo/riopa-infrastructure/actions/runs/30682545414) | Repository CI | None; hosted checks are necessary but do not replace external evidence |

The approved pilot scope, source exclusions and Zenodo preservation identifier
are recorded in `docs/wp010-bounded-pilot-decision.md`.

## Operating rule

Repository implementation may proceed while a gate is open when the affected
scope remains bounded and non-authoritative. A gate may be marked closed only
when the stated artifact exists and its revision, rights, reviewer or authority
are recorded. No row in this register is a waiver.
