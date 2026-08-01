# External dependency and release-gate register

This register separates repository-owned work from evidence that requires an
independent party, source custodian, preservation service or named release authority.
It is a planning and handoff artifact, not an approval record.

The current recommended regional-first technical-preview posture is recorded in
`docs/wp010-release-posture.md`; unresolved approvals remain explicitly TBD.

| Gate | Current state | Closure evidence | Responsible party | Fallback and promotion consequence |
|---|---|---|---|---|
| Independent WP-010 reproduction | Bounded pilot review passed with limitations via subagent; external gate remains open; issue [#149](https://github.com/edithatogo/riopa-infrastructure/issues/149) remains open | Pilot: report satisfying `docs/bounded-pilot-review-protocol.md`; beta/stable: external reviewer identity, environment, exact revision/bundle digest, commands, findings and signed/content-bound report | Pilot: qualified subagent; beta/stable: independent external person/operator | Pilot may remain internal/regional and non-operational; no beta, release-candidate or stable-release claim |
| Ambulance source authority | Regional pilot scope approved; national authority open | National authoritative source receipt and rights, or written approval of bounded regional scope; completed approval record before acquisition | Data custodian or programme owner | Pilot remains regional and non-operational; no national-completeness claim; request packet: `docs/source-authority-request-packet.md`; approval template: `docs/source-acquisition-approval-template.md` |
| Supermarket source rights | Partially bounded | Licence/terms record for every source and derived-output decision | Data steward and source custodian | Retain only rights-cleared OSM/aggregate outputs; exclude uncertain sources |
| Evidence preservation | Closed for WP-010 pilot packet | Zenodo DOI [`10.5281/zenodo.21735818`](https://doi.org/10.5281/zenodo.21735818), record URL, deposited packet SHA-256 and decision record | Preservation repository and programme owner | Successor packets require their own deposit and digest; this does not close beta/stable evidence gates |
| Release authority | Bounded pilot approved in decision record; beta/stable authority open | Named decision, scope, exclusions, expiry and accountable signatory for each promotion tier | Programme release authority | Pilot remains bounded/internal until preservation; no beta, tag or public stable release |
| Hosted verification | Passed for `ff328458f61fe8a5448979fcea04e4dbfba72afc` | CI run [30682545412](https://github.com/edithatogo/riopa-infrastructure/actions/runs/30682545412) and CodeQL run [30682545414](https://github.com/edithatogo/riopa-infrastructure/actions/runs/30682545414) | Repository CI | None; hosted checks are necessary but do not replace external evidence |

The approved pilot scope, source exclusions and Zenodo preservation identifier
are recorded in `docs/wp010-bounded-pilot-decision.md`.

## Operating rule

Repository implementation may proceed while a gate is open when the affected
scope remains bounded and non-authoritative. A gate may be marked closed only
when the stated artifact exists and its revision, rights, reviewer or authority
are recorded. No row in this register is a waiver.
