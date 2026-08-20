# Operational-cycle and soak evidence

`riopa_provenance.operational_cycles` provides a deterministic record format for
cycles containing timestamps, outcome, failure and recovery notes. It is a
recording tool only: it does not execute a deployment, wait for elapsed time,
or represent beta/RC operation.

The current status is `pending-duration` for the bounded preview. Synthetic
fixtures may exercise the schema, but the 90-day beta requirement and complete
failure/backfill/recovery cycles remain external operational evidence gates.
Any promotion must attach immutable raw observations and accountable release
authority records.
