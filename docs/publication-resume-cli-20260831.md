# Local publication recovery CLI

This WP-003 increment belongs to publication validation issue #129. It exposes
the existing exact-plan-bound recovery projection to operators and CI jobs:

```bash
uv run riopa publication resume --plan publication-plan.json \
  --state publication-state.json --receipts recovered-receipts.json
```

The plan and journal must be JSON objects. The optional receipts file must be a
JSON array; omitting it inspects the existing journal without adding receipts.
Each input must be a non-empty regular file of at most 8 MiB. Duplicate JSON
keys and non-finite JSON constants are rejected rather than silently selecting
or coercing a value.

On success the command writes only the key-sorted JSON projection to stdout
and exits zero. This means local reconciliation succeeded, not that publication
completed remotely. Invalid inputs fail nonzero with an error on stderr and no
projection. The command does not modify its input files, write a checkpoint,
read credentials or contact a provider. It has no output-file option.

The projection contains a detached `reconciled_state` and target dispositions:

- `receipt-recorded`: a locally validated receipt is present.
- `provider-reconciliation-required`: the provider's existing operation must be
  checked before deciding whether a separately authorized write is safe.

A missing receipt may mean a successful remote deposit lost its response. It is
not permission to create another release or DOI. `remote_write_authorized` stays
false, including when every receipt is recorded. Full plan-schema validation,
current rights, provider identity/immutability and stable qualification are not
established by this command.

Keep the original journal and recovered receipts as evidence. If capturing stdout
through shell redirection, use a new destination distinct from all inputs: the
shell can truncate a file before the command starts. Do not redirect into the
original journal. Receipt metadata is emitted in the projection; never put
credentials or sensitive payloads in these inputs or public logs.

The pure-core contract is described in
`docs/publication-plan-bound-resume-20260831.md`. Generalized authenticated
GitHub/Hugging Face/Zenodo adapters remain separate work; this CLI performs no
publication and does not close WP-003 or promote/archive the track.

## Validation and review

Implementation: `885bfc9`. On Python 3.14.5, 27 new recovery CLI tests and 33
existing CLI tests pass. Independent reviewers also ran the publication-core
tests, checking 93 and 126 tests respectively. The full suite passes 1,842 tests
with one skip and 90.62% branch-aware coverage against the approved 90% gate.
The full engineering quality harness passes, including lint, strict types,
configured security checks, schema/Conductor/issue validation and packaging.

One implementation subagent and two separately prompted review subagents found
no blocking findings after strict parsing, content-free errors and sorted JSON
output were incorporated. These are repository-owned advisory checks, not
provider acceptance or external human review. Hosted CI remains a separate
protected-merge requirement.
