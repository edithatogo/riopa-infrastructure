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

The `regional` object is measured. The `national` object is explicitly
`projection-not-measurement`; its linear extrapolation is informative only and
does not satisfy a national-scale qualification gate. Real national-scale
evidence requires an approved workload, infrastructure, resource/cost metrics,
and an immutable run log.
