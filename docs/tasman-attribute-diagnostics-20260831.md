# Tasman attribute-difference diagnostics

The first scheduled capture/publication chain reports 3,655 attribute-digest
differences against the fixed initial accepted packet, with no added, removed
or geometry-changed features. These are projected differences, not demonstrated
changes to planning policy or source data.

`scripts/diagnose_tasman_attribute_changes.py` compares the same verified
canonical snapshots and binds the existing comparison digest. It emits only
field names and changed-feature counts, separating `_riopa_`-prefixed fields
from other fields and indicating which the original comparator includes.
The prefix is a naming convention, not proof of field origin. Missing and null
values differ; nested changes count once at their top-level field. Added and
removed identities are counted separately from fields on shared identities.

`scripts/record_tasman_snapshot_comparison.py` writes the additional
`public/tasman-attribute-diagnostics.json` artifact using the already verified
baseline and current canonical files. It makes no additional network request.
Existing comparison receipts and public ledger schemas remain unchanged;
the diagnostic is not silently inserted into historical ledger hashes.

Unit and producer-hook tests cover binding failures, invalid lineage, field
classification, nested/null values, membership changes and fresh-output
requirements. Hosted diagnostic execution is separate evidence and is not
claimed by these tests. Neither field counts nor a manual replay qualify a new
scheduled source cycle, source-change causality, outage recovery or release.
