# Bounded lineage tutorial

Status: `bounded-rehearsal` — synthetic, offline and non-operational.

This tutorial demonstrates the positive lineage path and a fail-closed
troubleshooting path using only `examples/minimal/snapshot-manifest.json`.
It never contacts a live endpoint and does not create a release or publication
receipt.

## Run the tutorial

```sh
uv run python scripts/run_bounded_lineage_tutorial.py
```

The command prints a JSON report containing the imported snapshot identifier,
the disposable SQLite path, a query answer count and the expected
`failed-closed` missing-manifest diagnostic. To retain the disposable output
for inspection, pass `--output-dir /tmp/riopa-lineage-tutorial`.

## Verify the result

```sh
uv run pytest tests/test_bounded_lineage_tutorial.py -q
```

The test checks both the positive query path and the missing-manifest failure.
The fixture and its manifest remain the source-bound evidence; the SQLite file
is only a rebuildable query projection.

## Troubleshooting

- `manifest validation failed`: inspect the manifest closure and referenced
  files; do not substitute a live endpoint or repair source bytes in place.
- `unknown lineage node`: use an identifier present in the validated snapshot;
  missing coverage is not negative evidence.
- `failed-closed` on a missing or invalid file: provide a complete,
  content-addressed synthetic fixture and rerun the validation command.

Network, timetable, facility, national, clinical and dispatch claims remain
disabled. This tutorial cannot establish external-user/operator evidence,
production recovery, beta/RC soak or release-authority approval.
