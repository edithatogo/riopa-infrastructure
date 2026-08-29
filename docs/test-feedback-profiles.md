# Bounded test-feedback profiles

RIOPA keeps the complete clean-environment suite authoritative. Local profiles
are feedback accelerators only and must never be used to waive coverage,
mutation, rights, publication, or release gates.

## Profiles

Run the profile runner with Python 3.14 through `uv`:

```bash
uv run python scripts/run_test_profile.py fast
uv run python scripts/run_test_profile.py full
```

`fast` excludes tests marked `slow` or `serial`. Mark a test `serial` when it
mutates a shared file, database, environment, or other resource. The `full`
profile runs every test and is the required pre-commit/CI evidence command.

Optional experiments are deliberately dependency-gated and bounded:

```bash
uv run --with pytest-xdist python scripts/run_test_profile.py parallel --maxfail=1
uv run --with pytest-testmon python scripts/run_test_profile.py testmon
```

The parallel profile runs the non-serial tests with two workers, then runs the
serial phase. Increase `--workers` only after measuring resource use. Testmon
is opt-in; rebuild its local database after dependency or test-inventory
changes. Neither profile changes the clean CI command.

The runner prints a JSON observation containing each command, return code,
elapsed seconds, and collected-test count. Record before/after observations in
the issue or a dated evidence file when evaluating a change. Avoid brittle
wall-clock assertions: host load, filesystem and dependency caches affect
elapsed time.

Other experiments from issue #618 remain intentionally opt-in: import-time
and Scalene profiling, pytest-gremlins on a bounded core target, pytest-
benchmark for comparative measurements, redacted VCR cassettes for public
replay-safe HTTP only, immutable/in-memory database fixtures, and the coverage
`sysmon` core where its plugin/concurrency constraints are compatible. Never
record credentials or restricted payloads.
