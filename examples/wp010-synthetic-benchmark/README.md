# WP-010 synthetic methods benchmark

This fixed, dependency-free benchmark checks a small FCFS capacity calculation
and a difference-in-differences contrast. It is a correctness and handoff
fixture, not an empirical ambulance, hospital, supermarket, clinical, legal or
commercial analysis.

Run it from a clean checkout with:

```sh
python examples/wp010-synthetic-benchmark/verify.py
```

The verifier uses only the Python standard library and independently recomputes
the committed expected values. A successful run is repository-owned
reproduction evidence; it is not the external reproduction required for M5/M6.
