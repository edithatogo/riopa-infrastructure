import importlib.util
from pathlib import Path


def _runner():
    path = Path(__file__).parents[1] / "scripts/run_local_recovery_rehearsal.py"
    spec = importlib.util.spec_from_file_location("local_recovery_rehearsal", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_local_recovery_rehearsal_is_explicitly_bounded() -> None:
    report = _runner().run()
    assert report["status"] == "passed"
    assert report["classification"] == "repository-rehearsal-not-operational-evidence"
    assert [item["operation"] for item in report["operations"]] == [
        "snapshot",
        "restore",
        "rollback",
    ]
    assert report["safety"]["provider_contacted"] is False
    assert report["safety"]["deployment_mutated"] is False
    assert report["safety"]["independent_target"] is False
