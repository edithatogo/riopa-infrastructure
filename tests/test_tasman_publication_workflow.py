from pathlib import Path

import yaml


def test_publication_workflow_is_bounded_and_separate_from_capture() -> None:
    root = Path(__file__).resolve().parents[1]
    workflow = yaml.safe_load((root / ".github/workflows/tasman-publication.yml").read_text())
    triggers = workflow.get("on", workflow.get(True))
    assert triggers["workflow_run"] == {
        "workflows": ["Preserve bounded council archives"],
        "types": ["completed"],
    }
    assert workflow["permissions"] == {"contents": "read"}
    assert workflow["concurrency"]["group"].endswith("${{ github.run_id }}")
    job = workflow["jobs"]["publish"]
    assert "github.ref == 'refs/heads/main'" in job["if"]
    assert "github.event.workflow_run.head_branch == 'main'" in job["if"]
    assert "github.event.workflow_run.conclusion == 'success'" in job["if"]
    assert "head_repository.full_name == github.repository" in job["if"]
    assert job["timeout-minutes"] == 30
    assert job["concurrency"] == {
        "group": "tasman-publication-writer",
        "cancel-in-progress": False,
    }
    assert job["env"]["HF_HUB_DISABLE_IMPLICIT_TOKEN"] == "1"
    assert "HF_TOKEN" not in job["env"]
    steps = job["steps"]
    credential_steps = [step for step in steps if "HF_TOKEN" in step.get("env", {})]
    assert len(credential_steps) == 1
    assert credential_steps[0]["run"] == (
        "uv run python scripts/publish_tasman_public_packet.py "
        '--source-run "$SOURCE_RUN" --work "$WORK"'
    )
    assert not any("capture_tasman_catalogue.py" in s.get("run", "") for s in steps)
    artifact = steps[-1]
    assert artifact["with"]["path"] == f"{job['env']['WORK']}/public/"
    assert artifact["if"] == "${{ !cancelled() }}"
