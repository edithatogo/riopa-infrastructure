"""Deterministic noise-aware regression gates for repeated benchmarks."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from statistics import median


class BenchmarkGateError(ValueError):
    """Raised when benchmark samples cannot support a comparison."""


@dataclass(frozen=True)
class BenchmarkGateResult:
    baseline_median: float
    current_median: float
    baseline_mad: float
    allowed_change: float
    passed: bool
    reason: str


def _samples(values: Sequence[float], *, label: str, minimum: int) -> list[float]:
    if len(values) < minimum:
        raise BenchmarkGateError(f"{label} requires at least {minimum} samples")
    result = [float(value) for value in values]
    if any(not math.isfinite(value) or value <= 0 for value in result):
        raise BenchmarkGateError(f"{label} samples must be finite and positive")
    return result


def evaluate_regression(
    baseline: Sequence[float],
    current: Sequence[float],
    *,
    relative_tolerance: float = 0.10,
    higher_is_better: bool = False,
    minimum_samples: int = 3,
) -> BenchmarkGateResult:
    """Compare repeated samples using median plus a robust MAD allowance.

    For latency-like metrics ``higher_is_better`` is false; throughput-like
    metrics can set it true.  This is a local candidate gate, not hosted or
    national-scale qualification.
    """

    if not math.isfinite(relative_tolerance) or relative_tolerance < 0:
        raise BenchmarkGateError("relative_tolerance must be finite and non-negative")
    old = _samples(baseline, label="baseline", minimum=minimum_samples)
    new = _samples(current, label="current", minimum=minimum_samples)
    old_median = float(median(old))
    new_median = float(median(new))
    old_mad = float(median([abs(value - old_median) for value in old]))
    allowed = old_median * relative_tolerance + 3 * old_mad
    difference = new_median - old_median
    passed = difference <= allowed if not higher_is_better else -difference <= allowed
    direction = "increase" if not higher_is_better else "decrease"
    reason = (
        f"median {direction} {abs(difference):.6g} within allowance {allowed:.6g}"
        if passed
        else f"median {direction} {abs(difference):.6g} exceeds allowance {allowed:.6g}"
    )
    return BenchmarkGateResult(old_median, new_median, old_mad, allowed, passed, reason)
