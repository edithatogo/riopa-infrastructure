"""Inspectable exhaustive reference solvers for small facility-location problems."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from itertools import combinations, product
from math import isclose, isfinite
from typing import Literal

Model = Literal["set-cover", "maximal-cover", "p-median", "p-center"]


@dataclass(frozen=True)
class Demand:
    demand_id: str
    weight: float = 1.0
    subgroup: str = "all"

    def __post_init__(self) -> None:
        if not self.demand_id or self.weight <= 0:
            raise ValueError("demand requires a non-empty id and positive weight")


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    capacity: float | None = None
    opening_cost: float = 1.0
    fixed: bool = False
    eligible_demand: frozenset[str] | None = None

    def __post_init__(self) -> None:
        if not self.candidate_id or (self.capacity is not None and self.capacity <= 0):
            raise ValueError("candidate requires a non-empty id and positive capacity")
        if self.opening_cost < 0:
            raise ValueError("opening cost must be non-negative")


@dataclass(frozen=True)
class EquityConstraint:
    """An explicit upper bound on one subgroup's weighted mean distance."""

    subgroup: str
    max_mean_distance: float

    def __post_init__(self) -> None:
        if self.max_mean_distance < 0:
            raise ValueError("equity distance bound must be non-negative")


@dataclass(frozen=True)
class LocationProblem:
    model: Model
    demands: tuple[Demand, ...]
    candidates: tuple[Candidate, ...]
    travel: Mapping[tuple[str, str], float]
    p: int | None = None
    coverage_threshold: float | None = None
    budget: float | None = None
    equity_constraints: tuple[EquityConstraint, ...] = ()

    def __post_init__(self) -> None:
        demand_ids = [d.demand_id for d in self.demands]
        candidate_ids = [c.candidate_id for c in self.candidates]
        if not self.demands or not self.candidates:
            raise ValueError("problem requires demand and candidate records")
        if len(set(demand_ids)) != len(demand_ids) or len(set(candidate_ids)) != len(candidate_ids):
            raise ValueError("demand and candidate ids must be unique")
        if self.model in {"maximal-cover", "p-median", "p-center"} and self.p is None:
            raise ValueError(f"{self.model} requires p")
        if self.p is not None and self.p < sum(candidate.fixed for candidate in self.candidates):
            raise ValueError("p cannot be smaller than the number of fixed candidates")
        if self.model in {"set-cover", "maximal-cover"} and self.coverage_threshold is None:
            raise ValueError(f"{self.model} requires coverage_threshold")
        if self.coverage_threshold is not None and self.coverage_threshold < 0:
            raise ValueError("coverage threshold must be non-negative")
        if self.budget is not None and self.budget < 0:
            raise ValueError("budget must be non-negative")
        if any(value < 0 for value in self.travel.values()):
            raise ValueError("travel impedance must be non-negative")


@dataclass(frozen=True)
class LocationSolution:
    model: Model
    selected: tuple[str, ...]
    assignments: tuple[tuple[str, str], ...]
    covered: tuple[str, ...]
    objective: float
    subgroup_mean_distance: tuple[tuple[str, float], ...]
    solver: str = "riopa-exhaustive-reference"
    status: str = "optimal"
    bound: float | None = None
    gap: float = 0.0
    tolerance: float = 1e-9
    seed: int | None = None


@dataclass(frozen=True)
class Verification:
    valid: bool
    errors: tuple[str, ...]
    recomputed_objective: float | None


@dataclass(frozen=True)
class RobustScenario:
    """A bounded deterministic perturbation of a reference problem."""

    scenario_id: str
    travel_delta: Mapping[tuple[str, str], float] = field(default_factory=dict)
    demand_multiplier: Mapping[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.scenario_id.strip():
            raise ValueError("scenario_id must be non-empty")
        if any(not isfinite(value) for value in self.travel_delta.values()):
            raise ValueError("travel deltas must be finite")
        if any(not isfinite(value) or value < 0 for value in self.demand_multiplier.values()):
            raise ValueError("demand multipliers must be finite and non-negative")


@dataclass(frozen=True)
class ScenarioEvaluation:
    scenario_id: str
    solution: LocationSolution | None
    error: str | None = None


@dataclass(frozen=True)
class MultiPeriodPlan:
    """Explicit period-to-problem interface for bounded independent solves."""

    periods: tuple[str, ...]
    problems: Mapping[str, LocationProblem]

    def __post_init__(self) -> None:
        if not self.periods or len(set(self.periods)) != len(self.periods):
            raise ValueError("periods must be non-empty and unique")
        if set(self.problems) != set(self.periods):
            raise ValueError("problems must provide exactly one problem per period")

    def solve(self) -> tuple[tuple[str, LocationSolution], ...]:
        """Solve each period independently in declared period order."""

        return tuple((period, solve(self.problems[period])) for period in self.periods)


def evaluate_robust_scenarios(
    problem: LocationProblem, scenarios: tuple[RobustScenario, ...]
) -> tuple[ScenarioEvaluation, ...]:
    """Evaluate deterministic perturbations without probability or forecast claims."""

    if len({scenario.scenario_id for scenario in scenarios}) != len(scenarios):
        raise ValueError("scenario IDs must be unique")
    evaluations: list[ScenarioEvaluation] = []
    for scenario in scenarios:
        travel = dict(problem.travel)
        for pair, delta in scenario.travel_delta.items():
            if pair not in travel or travel[pair] + delta < 0:
                evaluations.append(
                    ScenarioEvaluation(scenario.scenario_id, None, "scenario travel is invalid")
                )
                break
            travel[pair] += delta
        else:
            demands = tuple(
                replace(
                    demand,
                    weight=demand.weight * scenario.demand_multiplier.get(demand.demand_id, 1.0),
                )
                for demand in problem.demands
            )
            try:
                solution = solve(replace(problem, demands=demands, travel=travel))
            except ValueError as error:
                evaluations.append(ScenarioEvaluation(scenario.scenario_id, None, str(error)))
            else:
                evaluations.append(ScenarioEvaluation(scenario.scenario_id, solution))
    return tuple(evaluations)


def _eligible(problem: LocationProblem, demand: Demand, candidate: Candidate) -> bool:
    return (
        candidate.eligible_demand is None or demand.demand_id in candidate.eligible_demand
    ) and (demand.demand_id, candidate.candidate_id) in problem.travel


def _candidate_subsets(problem: LocationProblem) -> tuple[tuple[Candidate, ...], ...]:
    fixed = tuple(candidate for candidate in problem.candidates if candidate.fixed)
    optional = tuple(candidate for candidate in problem.candidates if not candidate.fixed)
    maximum = len(problem.candidates) if problem.p is None else problem.p
    subsets: list[tuple[Candidate, ...]] = []
    for optional_count in range(maximum - len(fixed) + 1):
        for next_selection in combinations(optional, optional_count):
            selected = tuple(sorted((*fixed, *next_selection), key=lambda item: item.candidate_id))
            if problem.model != "set-cover" and len(selected) != problem.p:
                continue
            if (
                problem.budget is not None
                and sum(item.opening_cost for item in selected) > problem.budget
            ):
                continue
            subsets.append(selected)
    return tuple(subsets)


def _assignment_options(
    problem: LocationProblem, selected: tuple[Candidate, ...]
) -> tuple[tuple[str | None, ...], ...] | None:
    options: list[tuple[str | None, ...]] = []
    for demand in problem.demands:
        candidate_ids = tuple(
            candidate.candidate_id
            for candidate in selected
            if _eligible(problem, demand, candidate)
        )
        if problem.model == "maximal-cover":
            options.append((*candidate_ids, None))
        else:
            options.append(candidate_ids)
    if any(not item for item in options):
        return None
    return tuple(options)


def _metrics(
    problem: LocationProblem,
    assignments: tuple[tuple[str, str], ...],
) -> tuple[tuple[str, ...], float, float, tuple[tuple[str, float], ...]]:
    assignment_map = dict(assignments)
    covered = tuple(
        sorted(
            demand.demand_id
            for demand in problem.demands
            if demand.demand_id in assignment_map
            and (
                problem.coverage_threshold is None
                or problem.travel[(demand.demand_id, assignment_map[demand.demand_id])]
                <= problem.coverage_threshold
            )
        )
    )
    distances = {
        demand.demand_id: problem.travel[(demand.demand_id, assignment_map[demand.demand_id])]
        for demand in problem.demands
        if demand.demand_id in assignment_map
    }
    weighted_sum = sum(
        demand.weight * distances[demand.demand_id]
        for demand in problem.demands
        if demand.demand_id in distances
    )
    worst = max(distances.values(), default=0.0)
    subgroup_means: list[tuple[str, float]] = []
    for subgroup in sorted({demand.subgroup for demand in problem.demands}):
        members = [
            demand
            for demand in problem.demands
            if demand.subgroup == subgroup and demand.demand_id in distances
        ]
        total_weight = sum(member.weight for member in members)
        if total_weight:
            mean = (
                sum(member.weight * distances[member.demand_id] for member in members)
                / total_weight
            )
            subgroup_means.append((subgroup, mean))
    return covered, weighted_sum, worst, tuple(subgroup_means)


def _feasible_assignments(
    problem: LocationProblem, selected: tuple[Candidate, ...]
) -> tuple[tuple[tuple[str, str], ...], ...]:
    options = _assignment_options(problem, selected)
    if options is None:
        return ()
    feasible: list[tuple[tuple[str, str], ...]] = []
    candidate_map = {candidate.candidate_id: candidate for candidate in selected}
    for choices in product(*options):
        assignments = tuple(
            (demand.demand_id, choice)
            for demand, choice in zip(problem.demands, choices, strict=True)
            if choice is not None
        )
        loads = {
            candidate_id: sum(
                demand.weight
                for demand in problem.demands
                if (demand.demand_id, candidate_id) in assignments
            )
            for candidate_id in candidate_map
        }
        if any(
            candidate.capacity is not None and loads[candidate_id] > candidate.capacity
            for candidate_id, candidate in candidate_map.items()
        ):
            continue
        covered, _, _, subgroup_means = _metrics(problem, assignments)
        if problem.model == "set-cover" and len(covered) != len(problem.demands):
            continue
        if any(
            dict(subgroup_means).get(rule.subgroup, float("inf")) > rule.max_mean_distance
            for rule in problem.equity_constraints
        ):
            continue
        feasible.append(assignments)
    return tuple(feasible)


def solve(problem: LocationProblem) -> LocationSolution:
    """Solve a small problem exactly by deterministic exhaustive enumeration."""

    alternatives: list[tuple[tuple[float, ...], LocationSolution]] = []
    total_weight = sum(demand.weight for demand in problem.demands)
    for selected in _candidate_subsets(problem):
        for assignments in _feasible_assignments(problem, selected):
            covered, weighted_sum, worst, subgroup_means = _metrics(problem, assignments)
            selected_ids = tuple(candidate.candidate_id for candidate in selected)
            rank: tuple[float, ...]
            if problem.model == "set-cover":
                objective = sum(candidate.opening_cost for candidate in selected)
                rank = (objective, float(len(selected)), weighted_sum)
            elif problem.model == "maximal-cover":
                objective = sum(
                    demand.weight for demand in problem.demands if demand.demand_id in covered
                )
                rank = (-objective, weighted_sum)
            elif problem.model == "p-median":
                objective = weighted_sum / total_weight
                rank = (objective,)
            else:
                objective = worst
                rank = (objective, weighted_sum)
            solution = LocationSolution(
                model=problem.model,
                selected=selected_ids,
                assignments=assignments,
                covered=covered,
                objective=objective,
                subgroup_mean_distance=subgroup_means,
                bound=objective,
            )
            alternatives.append((rank, solution))
    if not alternatives:
        raise ValueError("problem is infeasible under the supplied constraints")
    return min(
        alternatives,
        key=lambda item: (item[0], item[1].selected, item[1].assignments),
    )[1]


def verify_solution(problem: LocationProblem, solution: LocationSolution) -> Verification:
    """Independently recalculate feasibility and objective from the public contract."""

    errors: list[str] = []
    if solution.model != problem.model:
        errors.append("solution model does not match problem")
    selected_map = {candidate.candidate_id: candidate for candidate in problem.candidates}
    if len(set(solution.selected)) != len(solution.selected):
        errors.append("selected candidate ids are not unique")
    if any(candidate_id not in selected_map for candidate_id in solution.selected):
        errors.append("solution selects an unknown candidate")
    if any(
        candidate.fixed and candidate.candidate_id not in solution.selected
        for candidate in problem.candidates
    ):
        errors.append("solution omits a fixed candidate")
    if (
        problem.p is not None
        and problem.model == "set-cover"
        and len(solution.selected) > problem.p
    ):
        errors.append("set-cover solution selects more than p candidates")
    if (
        problem.p is not None
        and problem.model != "set-cover"
        and len(solution.selected) != problem.p
    ):
        errors.append("solution does not select exactly p candidates")
    selected = tuple(
        selected_map[candidate_id]
        for candidate_id in solution.selected
        if candidate_id in selected_map
    )
    if problem.budget is not None and sum(item.opening_cost for item in selected) > problem.budget:
        errors.append("solution exceeds budget")
    demand_map = {demand.demand_id: demand for demand in problem.demands}
    assignments = dict(solution.assignments)
    if len(assignments) != len(solution.assignments):
        errors.append("solution assigns a demand more than once")
    structurally_valid_assignments: list[tuple[str, str]] = []
    for demand_id, candidate_id in solution.assignments:
        if (
            demand_id not in demand_map
            or candidate_id not in solution.selected
            or candidate_id not in selected_map
        ):
            errors.append("solution contains an unknown or unselected assignment")
        elif not _eligible(problem, demand_map[demand_id], selected_map[candidate_id]):
            errors.append("solution contains an ineligible assignment")
        else:
            structurally_valid_assignments.append((demand_id, candidate_id))
    for candidate in selected:
        load = sum(
            demand_map[demand_id].weight
            for demand_id, candidate_id in solution.assignments
            if demand_id in demand_map and candidate_id == candidate.candidate_id
        )
        if candidate.capacity is not None and load > candidate.capacity:
            errors.append(f"capacity exceeded for {candidate.candidate_id}")
    covered, weighted_sum, worst, subgroup_means = _metrics(
        problem, tuple(structurally_valid_assignments)
    )
    if covered != tuple(sorted(solution.covered)):
        errors.append("reported covered demands do not match assignments")
    if problem.model == "set-cover" and len(covered) != len(problem.demands):
        errors.append("set-cover solution leaves demand uncovered")
    if any(
        dict(subgroup_means).get(rule.subgroup, float("inf")) > rule.max_mean_distance
        for rule in problem.equity_constraints
    ):
        errors.append("equity constraint violated")
    if problem.model == "set-cover":
        recomputed = sum(candidate.opening_cost for candidate in selected)
    elif problem.model == "maximal-cover":
        recomputed = sum(demand.weight for demand in problem.demands if demand.demand_id in covered)
    elif problem.model == "p-median":
        recomputed = weighted_sum / sum(demand.weight for demand in problem.demands)
    else:
        recomputed = worst
    if not isclose(solution.objective, recomputed, abs_tol=solution.tolerance):
        errors.append("reported objective does not match recomputed objective")
    if subgroup_means != solution.subgroup_mean_distance:
        errors.append("reported subgroup means do not match assignments")
    return Verification(not errors, tuple(errors), recomputed)


def pareto_alternatives(problem: LocationProblem) -> tuple[LocationSolution, ...]:
    """Return deterministic non-dominated mean, worst and subgroup-gap alternatives."""

    if problem.model not in {"p-median", "p-center"}:
        raise ValueError("Pareto alternatives require a p-median or p-center problem")
    alternatives: list[tuple[tuple[float, float, float], LocationSolution]] = []
    total_weight = sum(demand.weight for demand in problem.demands)
    for selected in _candidate_subsets(problem):
        for assignments in _feasible_assignments(problem, selected):
            covered, weighted_sum, worst, subgroup_means = _metrics(problem, assignments)
            means = tuple(value for _, value in subgroup_means)
            gap = max(means, default=0.0) - min(means, default=0.0)
            metrics = (weighted_sum / total_weight, worst, gap)
            solution = LocationSolution(
                model=problem.model,
                selected=tuple(candidate.candidate_id for candidate in selected),
                assignments=assignments,
                covered=covered,
                objective=metrics[0] if problem.model == "p-median" else metrics[1],
                subgroup_mean_distance=subgroup_means,
                bound=metrics[0] if problem.model == "p-median" else metrics[1],
            )
            alternatives.append((metrics, solution))
    frontier = [
        (metrics, solution)
        for metrics, solution in alternatives
        if not any(
            all(other[index] <= metrics[index] for index in range(3))
            and any(other[index] < metrics[index] for index in range(3))
            for other, _ in alternatives
        )
    ]
    return tuple(
        solution
        for _, solution in sorted(
            frontier,
            key=lambda item: (item[0], item[1].selected, item[1].assignments),
        )
    )


def minimax_subgroup_alternative(problem: LocationProblem) -> LocationSolution:
    """Select the feasible solution that minimises the worst subgroup mean.

    The returned solution retains the problem's ordinary objective so the
    independent verifier can validate it without silently changing the
    mathematical model.  The selection rule is an explicit equity alternative,
    not a replacement for the model's primary objective or a policy judgment.
    """

    if problem.model not in {"p-median", "p-center"}:
        raise ValueError("minimax subgroup alternatives require a p-median or p-center problem")
    alternatives: list[LocationSolution] = []
    for selected in _candidate_subsets(problem):
        for assignments in _feasible_assignments(problem, selected):
            covered, weighted_sum, worst, subgroup_means = _metrics(problem, assignments)
            total_weight = sum(demand.weight for demand in problem.demands)
            objective = weighted_sum / total_weight if problem.model == "p-median" else worst
            alternatives.append(
                LocationSolution(
                    model=problem.model,
                    selected=tuple(candidate.candidate_id for candidate in selected),
                    assignments=assignments,
                    covered=covered,
                    objective=objective,
                    subgroup_mean_distance=subgroup_means,
                    bound=objective,
                )
            )
    if not alternatives:
        raise ValueError("problem is infeasible under the supplied constraints")
    return min(
        alternatives,
        key=lambda solution: (
            max((mean for _, mean in solution.subgroup_mean_distance), default=0.0),
            solution.objective,
            solution.selected,
            solution.assignments,
        ),
    )
