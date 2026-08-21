# Planning transition downstream contract

`tests/test_transition_downstream.py` is the bounded integration contract for
using a planning transition in downstream reference analysis. It selects the
replacement transition at an explicit `valid_time` perspective, retains the
successor plan identifier for a zoning lookup, and passes that identifier to
the dependency-free accessibility measure.

The fixture is synthetic and exercises only identifier continuity and arithmetic
selection. It does not provide a council source capture, legal equivalence,
road network, timetable, facility registry, national coverage or operational
accessibility evidence. Those claims remain disabled until their separately
archived public sources and gates exist.
