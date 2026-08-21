import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_alert_contract_has_owner_and_action_for_each_signal() -> None:
    record = json.loads((ROOT / "docs/operations-alert-contract-20260822.json").read_text())
    assert {item["signal"] for item in record["alerts"]} == {
        "source_health",
        "freshness",
        "quality",
    }
    assert all(item["owner_role"] and item["action"] for item in record["alerts"])


def test_alert_suppression_is_expiring_and_fail_closed() -> None:
    suppression = json.loads((ROOT / "docs/operations-alert-contract-20260822.json").read_text())[
        "suppression"
    ]
    assert suppression["default"] == "do-not-suppress"
    assert set(suppression["required_fields"]) >= {
        "reason",
        "started_at",
        "expires_at",
        "owner_role",
    }
