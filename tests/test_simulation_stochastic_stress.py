from __future__ import annotations

import pytest

from riopa_provenance.facility_location import (
    Candidate,
    Demand,
    LocationProblem,
    stochastic_stress_test,
)


def _problem() -> LocationProblem:
    return LocationProblem(
        model="p-median",
        demands=(Demand("rural", subgroup="rural"), Demand("urban", subgroup="urban")),
        candidates=(Candidate("west"), Candidate("east")),
        travel={
            ("rural", "west"): 0.0,
            ("rural", "east"): 4.0,
            ("urban", "west"): 4.0,
            ("urban", "east"): 0.0,
        },
        p=1,
    )


def test_stochastic_stress_packet_is_reproducible_and_bounded() -> None:
    packet = stochastic_stress_test(
        _problem(), seed=7, replications=4, travel_jitter=0.2, demand_jitter=0.1
    )
    assert packet == stochastic_stress_test(
        _problem(), seed=7, replications=4, travel_jitter=0.2, demand_jitter=0.1
    )
    assert packet["successful_replications"] == 4
    assert packet["promotion_allowed"] is False
    assert packet["claim_classification"] == "synthetic-stress-rehearsal"


@pytest.mark.parametrize(
    "kwargs", [{"replications": 0}, {"travel_jitter": -1.0}, {"demand_jitter": 1.1}]
)
def test_stochastic_stress_rejects_invalid_controls(kwargs: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        stochastic_stress_test(_problem(), seed=7, **kwargs)
