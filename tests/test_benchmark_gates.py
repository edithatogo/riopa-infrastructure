import pytest

from riopa_provenance.benchmark_gates import BenchmarkGateError, evaluate_regression


def test_noise_aware_gate_accepts_small_jitter() -> None:
    result = evaluate_regression([100, 101, 99, 100], [102, 100, 101, 103])
    assert result.passed is True
    assert result.baseline_median == 100
    assert result.baseline_mad == 0.5


def test_noise_aware_gate_rejects_material_latency_regression() -> None:
    result = evaluate_regression([100, 101, 99], [140, 142, 141])
    assert result.passed is False
    assert "exceeds allowance" in result.reason


def test_throughput_direction_is_explicit_and_invalid_samples_fail() -> None:
    result = evaluate_regression([100, 101, 99], [95, 100, 96], higher_is_better=True)
    assert result.passed is True
    with pytest.raises(BenchmarkGateError, match="at least 3"):
        evaluate_regression([1, 2], [1, 2])
    with pytest.raises(BenchmarkGateError, match="finite and positive"):
        evaluate_regression([1, 0, 1], [1, 1, 1])
