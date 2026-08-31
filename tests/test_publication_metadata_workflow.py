import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_metadata_request_matches_exact_historical_public_mirror() -> None:
    request = json.loads(
        (ROOT / "docs/publication-provider-metadata-request-20260831.json").read_text()
    )
    receipt = json.loads((ROOT / "docs/v0.4.0-release-mirror-20260829.json").read_text())
    mirror = receipt["mirror"]
    assert receipt["qualification"]["status"] == "published_and_publicly_reverified"
    assert mirror["provider"] == "huggingface"
    assert request == {
        "schema_version": "1.0.0",
        "provider": "hugging-face",
        "repository": mirror["repository"],
        "revision": mirror["commit"],
        "path": mirror["path"] + "/release-metadata.json",
        "sha256": mirror["release_metadata_sha256"],
        "max_bytes": 2 * 1024 * 1024,
    }
    assert re.fullmatch(r"[0-9a-f]{40}", request["revision"])
    assert re.fullmatch(r"[0-9a-f]{64}", request["sha256"])


def test_metadata_workflow_is_main_only_fixed_read_only_and_retains_failures() -> None:
    text = (ROOT / ".github/workflows/reconcile-publication-metadata.yml").read_text()
    workflow = yaml.safe_load(text)
    assert workflow.get("on", workflow.get(True)) == {"workflow_dispatch": None}
    assert workflow["permissions"] == {"contents": "read"}
    assert "secrets." not in text and "github.token" not in text
    assert "HF_TOKEN" not in text and "GH_TOKEN" not in text
    assert set(workflow["jobs"]) == {"reconcile"}
    job = workflow["jobs"]["reconcile"]
    assert job["if"] == (
        "github.repository == 'edithatogo/riopa-infrastructure' && github.ref == 'refs/heads/main'"
    )
    assert "permissions" not in job
    assert job["timeout-minutes"] == 5
    assert job["env"] == {
        "HF_HUB_DISABLE_IMPLICIT_TOKEN": "1",
        "HF_HUB_DISABLE_TELEMETRY": "1",
        "HF_HUB_DOWNLOAD_TIMEOUT": "15",
        "HF_HUB_ETAG_TIMEOUT": "15",
    }
    steps = job["steps"]
    assert steps[0]["with"]["persist-credentials"] is False
    assert steps[1]["with"] == {"python-version": "3.14", "version": "0.11.16"}
    assert all("env" not in step for step in steps)
    assert all(
        re.fullmatch(r"[^@]+@[0-9a-f]{40}", step["uses"]) for step in steps if "uses" in step
    )
    runs = [step for step in steps if "run" in step]
    assert len(runs) == 1 and "if" not in runs[0]
    assert runs[0]["run"] == (
        "mkdir -p .riopa-local\n"
        "uv run --locked --extra preservation python "
        "scripts/reconcile_publication_provider_metadata.py \\\n"
        "  --request docs/publication-provider-metadata-request-20260831.json \\\n"
        "  > .riopa-local/publication-provider-metadata.json\n"
    )
    artifact = steps[-1]
    assert artifact["uses"].startswith("actions/upload-artifact@")
    assert artifact["if"] == "always()"
    assert artifact["with"]["path"] == ".riopa-local/publication-provider-metadata.json"
    assert artifact["with"]["if-no-files-found"] == "error"
    assert artifact["with"]["retention-days"] == 90
    assert "github.run_id" in artifact["with"]["name"]
    assert "github.run_attempt" in artifact["with"]["name"]
