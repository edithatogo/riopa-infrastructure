# WP-010 issue #149 reconciliation

**Checked:** 2026-08-01  
**Status:** local reconciliation note; issue update not sent.

The open issue [#149](https://github.com/edithatogo/riopa-infrastructure/issues/149)
still names source revision `5e8a8a50f579a3a48d0045e4173b9b4f9f7bad67`, while the
current preserved handoff is frozen at `8cac8b019cd20f7ba276147567442003489ac5b5`.
The expected reviewer-bundle SHA remains the same:
`26bf2281f67c35f3327ebadeda3c8d5e7c6460e5b447dfc8417c851bcb0b6813`.

The external-operator handoff draft and internal preflight use the current
revision and should be the source of truth for any future issue update. Before
recruitment or execution, update issue #149 to reference:

- commit `8cac8b019cd20f7ba276147567442003489ac5b5`;
- the current preflight and operator-handoff documents;
- Zenodo successor DOI `10.5281/zenodo.21737563` as preservation context only;
- the unchanged reviewer-bundle digest.

This mismatch does not close or waive the external reproduction gate. No issue
comment or edit was sent as part of this reconciliation.
