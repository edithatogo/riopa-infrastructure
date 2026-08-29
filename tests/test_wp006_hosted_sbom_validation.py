import json
import re
from pathlib import Path


def test_wp006_hosted_sbom_receipt_is_exact_head_and_fail_closed() -> None:
    receipt = json.loads(Path("docs/wp006-hosted-sbom-validation-20260829.json").read_text())
    assert receipt["result"] == "passed"
    assert re.fullmatch(r"[0-9a-f]{40}", receipt["source_revision"])
    workflow = receipt["workflow"]
    assert workflow["event"] == "workflow_dispatch"
    assert workflow["conclusion"] == "success"
    assert workflow["strict_cyclonedx_step"] == "success"
    assert str(workflow["run_id"]) in workflow["run_url"]
    assert re.fullmatch(r"sha256:[0-9a-f]{64}", receipt["artifact"]["digest"])
    assert receipt["artifact"]["expires_at"]
    assert receipt["limitations"]
