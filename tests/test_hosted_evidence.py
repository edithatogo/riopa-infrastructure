import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from scripts.record_hosted_evidence import LANES, run_lane

ROOT = Path(__file__).resolve().parents[1]


def test_hosted_receipt_is_content_bound_and_fail_closed(tmp_path: Path) -> None:
    receipt = run_lane("operational-observation", tmp_path)
    schema = json.loads((ROOT / "schemas/hosted-evidence.schema.json").read_text())
    Draft202012Validator(schema).validate(receipt)
    log = (tmp_path / receipt["log"]["path"]).read_bytes()
    assert receipt["log"]["sha256"] == hashlib.sha256(log).hexdigest()
    assert receipt["classification"] == "hosted-technical-preview-drill"
    assert len(receipt["non_claims"]) >= 4


def test_hosted_lanes_are_fixed_not_arbitrary_commands() -> None:
    assert set(LANES) == {
        "recovery-rollback",
        "agent-clean-room",
        "scale-smoke",
        "operational-observation",
        "rc-soak-observation",
    }
