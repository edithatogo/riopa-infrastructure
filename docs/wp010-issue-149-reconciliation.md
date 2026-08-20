# WP-010 issue #149 reconciliation

**Checked:** 2026-08-03
**Status:** repository handoff reconciled; external execution still pending.

The open issue [#149](https://github.com/edithatogo/riopa-infrastructure/issues/149)
still names older source revisions in historical comments, while the current
preserved handoff is frozen at `8cac8b019cd20f7ba276147567442003489ac5b5`.
The expected reviewer-bundle SHA remains the same:
`26bf2281f67c35f3327ebadeda3c8d5e7c6460e5b447dfc8417c851bcb0b6813`.

The external-operator handoff, request and report template now use the current
revision and should be the source of truth for recruitment or execution. Issue
#149 should reference:

- commit `8cac8b019cd20f7ba276147567442003489ac5b5`;
- the current preflight and operator-handoff documents;
- Zenodo successor DOI `10.5281/zenodo.21737563` as preservation context only;
- the unchanged reviewer-bundle digest.

This mismatch does not close or waive the external reproduction gate. No issue
comment or edit was sent as part of this reconciliation.
