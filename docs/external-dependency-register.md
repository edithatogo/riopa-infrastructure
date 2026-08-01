# External dependency and release-gate register

This register separates repository-owned work from evidence that requires an
independent party, source custodian, preservation service or named release authority.
It is a planning and handoff artifact, not an approval record.

| Gate | Current state | Closure evidence | Responsible party | Fallback and promotion consequence |
|---|---|---|---|---|
| Independent WP-010 reproduction | Open; issue [#149](https://github.com/edithatogo/riopa-infrastructure/issues/149) | Stable reviewer identity or pseudonym, environment, exact revision/bundle digest, commands, findings and signed/content-bound report | Independent reviewer or qualified independent analyst-agent | Internal verification only; no independent-reproduction or stable-release claim |
| Ambulance source authority | Open | National authoritative source receipt and rights, or written approval of bounded regional scope | Data custodian or programme owner | Keep the pilot regional and non-operational; no national-completeness claim |
| Supermarket source rights | Partially bounded | Licence/terms record for every source and derived-output decision | Data steward and source custodian | Retain only rights-cleared OSM/aggregate outputs; exclude uncertain sources |
| Evidence preservation | Open | Persistent deposit identifier, manifest, checksums, revision and access/withdrawal terms | Preservation repository and programme owner | Temporary evidence staging only; no preservation gate or stable release |
| Release authority | Open | Named decision, scope, exclusions, expiry and accountable signatory | Programme release authority | Pilot/internal status only; no tag or public stable release |
| Hosted verification | Passed for `ff328458f61fe8a5448979fcea04e4dbfba72afc` | CI run [30682545412](https://github.com/edithatogo/riopa-infrastructure/actions/runs/30682545412) and CodeQL run [30682545414](https://github.com/edithatogo/riopa-infrastructure/actions/runs/30682545414) | Repository CI | None; hosted checks are necessary but do not replace external evidence |

The proposed pilot scope and source exclusions are prepared in
`docs/wp010-bounded-pilot-decision.md`; its decision fields remain pending.

## Operating rule

Repository implementation may proceed while a gate is open when the affected
scope remains bounded and non-authoritative. A gate may be marked closed only
when the stated artifact exists and its revision, rights, reviewer or authority
are recorded. No row in this register is a waiver.
