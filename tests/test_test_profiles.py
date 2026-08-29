from __future__ import annotations

import importlib.util
from pathlib import Path

_SCRIPT = Path(__file__).parents[1] / "scripts" / "run_test_profile.py"
_SPEC = importlib.util.spec_from_file_location("run_test_profile", _SCRIPT)
assert _SPEC is not None and _SPEC.loader is not None
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)


def test_collected_count_accepts_singular_and_plural() -> None:
    assert _MODULE._collected("1 test collected in 0.01s") == 1
    assert _MODULE._collected("4 tests collected in 0.01s") == 4
    assert _MODULE._collected("no tests ran") is None


def test_fast_profile_excludes_slow_and_serial_and_forwards_args() -> None:
    commands = _MODULE._command("fast", 2, ["tests/test_ci_quality_gates.py"])
    assert commands == [
        [
            "uv",
            "run",
            "pytest",
            "--collect-only",
            "-m",
            "not slow and not serial",
            "tests/test_ci_quality_gates.py",
        ],
        [
            "uv",
            "run",
            "pytest",
            "-m",
            "not slow and not serial",
            "tests/test_ci_quality_gates.py",
        ],
    ]
