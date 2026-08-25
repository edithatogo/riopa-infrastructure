import json
from pathlib import Path


def test_profile_validation_receipt_is_bounded_and_fail_closed() -> None:
    root = Path(__file__).resolve().parents[1]
    report = json.loads(
        (root / "docs/research-object-profile-validation-20260825.json").read_text()
    )
    assert report["status"] == "bounded-tooling-validation"
    assert report["external_acceptance"] is False
    assert report["promotion_allowed"] is False
    assert all(check["passed"] for check in report["checks"])
    assert any("non-Python" in gate for gate in report["open_gates"])
