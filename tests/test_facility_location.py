from dataclasses import replace
from typing import cast

import pytest

from riopa_provenance.facility_location import (
    Candidate,
    Demand,
    EquityConstraint,
    LocationProblem,
    Model,
    minimax_subgroup_alternative,
    pareto_alternatives,
    solve,
    verify_solution,
)


def _line_problem(
    model: str, *, p: int | None = None, threshold: float | None = None
) -> LocationProblem:
    return LocationProblem(
        model=cast(Model, model),
        demands=(Demand("d0", subgroup="rural"), Demand("d4", subgroup="urban")),
        candidates=(Candidate("c0"), Candidate("c2"), Candidate("c4")),
        travel={
            ("d0", "c0"): 0,
            ("d0", "c2"): 2,
            ("d0", "c4"): 4,
            ("d4", "c0"): 4,
            ("d4", "c2"): 2,
            ("d4", "c4"): 0,
        },
        p=p,
        coverage_threshold=threshold,
    )


@pytest.mark.parametrize(
    ("model", "p", "threshold", "selected", "objective"),
    [
        ("set-cover", None, 2, ("c2",), 1.0),
        ("maximal-cover", 1, 1, ("c0",), 1.0),
        ("p-median", 1, None, ("c0",), 2.0),
        ("p-center", 1, None, ("c2",), 2.0),
    ],
)
def test_independently_calculated_line_benchmarks(
    model: str,
    p: int | None,
    threshold: float | None,
    selected: tuple[str, ...],
    objective: float,
) -> None:
    solution = solve(_line_problem(model, p=p, threshold=threshold))
    assert solution.selected == selected
    assert solution.objective == objective
    assert verify_solution(_line_problem(model, p=p, threshold=threshold), solution).valid


def test_capacity_fixed_budget_and_eligibility_are_enforced() -> None:
    problem = LocationProblem(
        model="p-median",
        demands=(Demand("a", 2), Demand("b", 2)),
        candidates=(
            Candidate("fixed", capacity=2, fixed=True, eligible_demand=frozenset({"a"})),
            Candidate("other", capacity=2, opening_cost=2),
        ),
        travel={
            ("a", "fixed"): 0,
            ("a", "other"): 3,
            ("b", "fixed"): 1,
            ("b", "other"): 0,
        },
        p=2,
        budget=3,
    )
    solution = solve(problem)
    assert solution.assignments == (("a", "fixed"), ("b", "other"))
    assert verify_solution(problem, solution).valid


def test_equity_constraint_changes_the_optimum_explicitly() -> None:
    unconstrained = LocationProblem(
        model="p-median",
        demands=(Demand("r", 1, "rural"), Demand("u", 4, "urban")),
        candidates=(Candidate("rural"), Candidate("urban")),
        travel={
            ("r", "rural"): 0,
            ("r", "urban"): 8,
            ("u", "rural"): 4,
            ("u", "urban"): 0,
        },
        p=1,
    )
    assert solve(unconstrained).selected == ("urban",)
    constrained = replace(unconstrained, equity_constraints=(EquityConstraint("rural", 4),))
    assert solve(constrained).selected == ("rural",)


def test_independent_verifier_catches_corruption() -> None:
    problem = _line_problem("p-median", p=1)
    solution = solve(problem)
    corrupted = replace(solution, objective=999, assignments=(("d0", "c2"), ("d4", "c0")))
    verification = verify_solution(problem, corrupted)
    assert not verification.valid
    assert "reported objective does not match recomputed objective" in verification.errors
    assert "solution contains an unknown or unselected assignment" in verification.errors


def test_pareto_frontier_is_deterministic_and_non_dominated() -> None:
    problem = LocationProblem(
        model="p-median",
        demands=(Demand("r", 1, "rural"), Demand("u", 3, "urban")),
        candidates=(Candidate("rural"), Candidate("middle"), Candidate("urban")),
        travel={
            ("r", "rural"): 0,
            ("r", "middle"): 3,
            ("r", "urban"): 8,
            ("u", "rural"): 6,
            ("u", "middle"): 3,
            ("u", "urban"): 0,
        },
        p=1,
    )
    frontier = pareto_alternatives(problem)
    assert tuple(item.selected for item in frontier) == (("urban",), ("middle",))
    assert frontier == pareto_alternatives(problem)


def test_minimax_subgroup_alternative_is_explicit_and_verifiable() -> None:
    problem = LocationProblem(
        model="p-median",
        demands=(Demand("r", 1, "rural"), Demand("u", 3, "urban")),
        candidates=(Candidate("rural"), Candidate("middle"), Candidate("urban")),
        travel={
            ("r", "rural"): 0,
            ("r", "middle"): 3,
            ("r", "urban"): 8,
            ("u", "rural"): 6,
            ("u", "middle"): 3,
            ("u", "urban"): 0,
        },
        p=1,
    )
    solution = minimax_subgroup_alternative(problem)
    assert solution.selected == ("middle",)
    assert verify_solution(problem, solution).valid


def test_infeasible_capacity_returns_bounded_explanation() -> None:
    problem = LocationProblem(
        model="set-cover",
        demands=(Demand("a", 2),),
        candidates=(Candidate("small", capacity=1),),
        travel={("a", "small"): 0},
        coverage_threshold=1,
    )
    with pytest.raises(ValueError, match="infeasible under the supplied constraints"):
        solve(problem)


def test_set_cover_p_is_an_upper_bound_in_solver_and_verifier() -> None:
    problem = _line_problem("set-cover", p=2, threshold=2)
    solution = solve(problem)
    assert solution.selected == ("c2",)
    assert verify_solution(problem, solution).valid


@pytest.mark.parametrize(
    "factory",
    [
        lambda: Demand("", 1),
        lambda: Demand("d", 0),
        lambda: Candidate("", 1),
        lambda: Candidate("c", 0),
        lambda: Candidate("c", opening_cost=-1),
        lambda: EquityConstraint("rural", -1),
        lambda: LocationProblem("p-median", (), (Candidate("c"),), {}, p=1),
        lambda: LocationProblem(
            "p-median",
            (Demand("d"), Demand("d")),
            (Candidate("c"),),
            {("d", "c"): 1},
            p=1,
        ),
        lambda: LocationProblem("p-median", (Demand("d"),), (Candidate("c"),), {("d", "c"): 1}),
        lambda: LocationProblem(
            "p-median",
            (Demand("d"),),
            (Candidate("c", fixed=True),),
            {("d", "c"): 1},
            p=0,
        ),
        lambda: LocationProblem("set-cover", (Demand("d"),), (Candidate("c"),), {("d", "c"): 1}),
        lambda: LocationProblem(
            "set-cover",
            (Demand("d"),),
            (Candidate("c"),),
            {("d", "c"): 1},
            coverage_threshold=-1,
        ),
        lambda: LocationProblem(
            "p-median",
            (Demand("d"),),
            (Candidate("c"),),
            {("d", "c"): 1},
            p=1,
            budget=-1,
        ),
        lambda: LocationProblem(
            "p-median",
            (Demand("d"),),
            (Candidate("c"),),
            {("d", "c"): -1},
            p=1,
        ),
    ],
)
def test_problem_contract_rejects_invalid_inputs(factory: object) -> None:
    with pytest.raises(ValueError):
        factory()  # type: ignore[operator]


def test_verifier_reports_independent_constraint_failures() -> None:
    problem = LocationProblem(
        model="p-median",
        demands=(Demand("a", 2, "priority"), Demand("b", 2)),
        candidates=(
            Candidate("fixed", capacity=2, fixed=True, eligible_demand=frozenset({"a"})),
            Candidate("other", capacity=2, opening_cost=2),
        ),
        travel={
            ("a", "fixed"): 0,
            ("a", "other"): 3,
            ("b", "fixed"): 1,
            ("b", "other"): 0,
        },
        p=2,
        budget=2,
        equity_constraints=(EquityConstraint("priority", 0),),
    )
    valid_shape = solve(replace(problem, budget=3))
    corrupted = replace(
        valid_shape,
        model="p-center",
        selected=("other", "other", "unknown"),
        assignments=(("a", "other"), ("a", "other"), ("missing", "other")),
        covered=("wrong",),
        subgroup_mean_distance=(),
    )
    verification = verify_solution(problem, corrupted)
    assert not verification.valid
    assert {
        "solution model does not match problem",
        "selected candidate ids are not unique",
        "solution selects an unknown candidate",
        "solution omits a fixed candidate",
        "solution does not select exactly p candidates",
        "solution exceeds budget",
        "solution assigns a demand more than once",
        "reported covered demands do not match assignments",
        "equity constraint violated",
        "reported subgroup means do not match assignments",
    }.issubset(verification.errors)


def test_verifier_reports_capacity_and_set_cover_limit_failures() -> None:
    problem = LocationProblem(
        model="set-cover",
        demands=(Demand("a", 2), Demand("b", 2)),
        candidates=(Candidate("x", capacity=2), Candidate("y")),
        travel={
            ("a", "x"): 0,
            ("a", "y"): 0,
            ("b", "x"): 0,
            ("b", "y"): 0,
        },
        p=1,
        coverage_threshold=1,
    )
    solution = solve(problem)
    corrupted = replace(
        solution,
        selected=("x", "y"),
        assignments=(("a", "x"), ("b", "x")),
        covered=("a",),
    )
    verification = verify_solution(problem, corrupted)
    assert "set-cover solution selects more than p candidates" in verification.errors
    assert "capacity exceeded for x" in verification.errors
    assert "set-cover solution leaves demand uncovered" not in verification.errors

    uncovered = replace(
        solution,
        assignments=(("a", "x"),),
        covered=("a",),
    )
    assert (
        "set-cover solution leaves demand uncovered" in verify_solution(problem, uncovered).errors
    )


def test_verifier_reports_ineligible_assignment() -> None:
    problem = LocationProblem(
        model="p-median",
        demands=(Demand("a"), Demand("b")),
        candidates=(
            Candidate("restricted", eligible_demand=frozenset({"a"})),
            Candidate("open"),
        ),
        travel={
            ("a", "restricted"): 0,
            ("a", "open"): 1,
            ("b", "restricted"): 0,
            ("b", "open"): 1,
        },
        p=2,
    )
    solution = solve(problem)
    corrupted = replace(
        solution,
        assignments=(("a", "restricted"), ("b", "restricted")),
    )
    assert (
        "solution contains an ineligible assignment" in verify_solution(problem, corrupted).errors
    )
    malformed = replace(solution, assignments=(("a", "unknown"),))
    verification = verify_solution(problem, malformed)
    assert not verification.valid
    assert "solution contains an unknown or unselected assignment" in verification.errors


def test_budget_can_make_problem_infeasible() -> None:
    problem = LocationProblem(
        model="p-median",
        demands=(Demand("a"),),
        candidates=(Candidate("expensive", opening_cost=2),),
        travel={("a", "expensive"): 0},
        p=1,
        budget=1,
    )
    with pytest.raises(ValueError, match="infeasible"):
        solve(problem)


def test_pareto_rejects_coverage_models() -> None:
    with pytest.raises(ValueError, match="require a p-median or p-center"):
        pareto_alternatives(_line_problem("set-cover", threshold=2))
