# WP-010 performance contract

This dependency-free runner defines the evidence shape for performance work
on the bounded, regional public-data pilot. It measures a deterministic
synthetic workload and records elapsed time, throughput, repetitions, checksum
and environment. It is a reproducibility harness, not an operational load
test.

```sh
python examples/wp010-performance-benchmark/run.py \
  --output /tmp/wp010-performance.json
```

The runner emits baseline, stressed and degraded regional scenarios. Each
scenario includes p50/p95 latency, throughput, and explicit resource/cost
instrumentation status (unavailable fields are `null`, never invented).

The workload is bound to the content-addressed national manifest at
`docs/national-workload-manifest-20260803.json`. Its archived Meshblock
geography and subnational population snapshot supply ingestion metadata and
the bounded scalability projection; the population snapshot is not joined or
downscaled to Meshblocks. Accessibility is reference-only for those archived
inputs. Network, timetable and facility claims remain disabled until their
corresponding archives exist.

The `regional` object is measured. The `national` object is explicitly
`projection-not-measurement`; its linear extrapolation is informative only and
does not satisfy a national-scale qualification gate. Real national-scale
evidence requires an approved workload, infrastructure, resource/cost metrics,
and an immutable run log.
