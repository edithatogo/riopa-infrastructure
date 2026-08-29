import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_hosted_beta_rc_observation_is_revision_bound_and_non_authorizing() -> None:
    record = json.loads(
        (ROOT / "docs/hosted-beta-rc-campaign-observation-20260829-ca3df8dc.json").read_text(
            encoding="utf-8"
        )
    )
    assert re.fullmatch(r"[0-9a-f]{40}", record["source_revision"])
    assert record["beta"]["status"] == "passed"
    assert record["rc"]["status"] == "passed"
    assert record["beta"]["run_id"] != record["rc"]["run_id"]
    assert record["beta"]["qualification_epoch"] != record["rc"]["qualification_epoch"]
    assert record["non_claims"]
    assert any("90-day" in claim for claim in record["non_claims"])
