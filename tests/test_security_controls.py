import json
import re
from pathlib import Path

import yaml


def test_security_control_manifest_is_bounded_and_complete() -> None:
    manifest = json.loads(Path("docs/security-control-manifest.json").read_text())
    assert manifest["status"] == "repository-baseline"
    assert {control["id"] for control in manifest["controls"]} == {
        "SC-01",
        "SC-02",
        "SC-03",
        "SC-04",
    }
    assert manifest["external_gates"]


def test_release_and_ci_actions_use_immutable_references() -> None:
    for path in Path(".github/workflows").glob("*.yml"):
        text = path.read_text()
        for use in re.findall(r"uses:\s*([^\s#]+)", text):
            assert "@" in use, f"unversioned action in {path}: {use}"
            ref = use.rsplit("@", 1)[1]
            if use.startswith(("actions/", "astral-sh/")):
                assert re.fullmatch(r"[0-9a-f]{40}", ref), f"mutable action ref in {path}: {use}"


def test_workflows_declare_fail_closed_least_privilege_permissions() -> None:
    allowed = {"read", "none"}
    release_write_allowlist = {
        "contents",
        "id-token",
        "attestations",
        "artifact-metadata",
    }
    for path in Path(".github/workflows").glob("*.yml"):
        document = yaml.safe_load(path.read_text())
        permissions = document.get("permissions")
        assert isinstance(permissions, dict), f"workflow lacks top-level permissions: {path}"
        for scope, value in permissions.items():
            assert value in allowed, f"unexpected top-level permission {scope}:{value} in {path}"
        for job_name, job in document.get("jobs", {}).items():
            if not isinstance(job, dict) or "permissions" not in job:
                continue
            job_permissions = job["permissions"]
            assert isinstance(job_permissions, dict), (
                f"job permissions must be explicit: {path}:{job_name}"
            )
            for scope, value in job_permissions.items():
                if scope == "security-events" and value == "write":
                    continue
                if path.name == "release.yml" and job_name == "publish" and value == "write":
                    assert scope in release_write_allowlist
                    continue
                assert value in allowed, (
                    f"unexpected job permission {scope}:{value} in {path}:{job_name}"
                )


def test_security_plan_closes_bounded_contracts_without_claiming_execution() -> None:
    plan = Path("conductor/tracks/security_supply_chain_20260719/plan.md").read_text()
    assert "[x] 3.1 Emit DSSE/in-toto-compatible" in plan
    assert "[x] 3.2 Define deterministic signing" in plan
    assert "[x] 4.1 Define a digest-bound orchestrated" in plan
    assert "[x] 4.2 Define and validate credential-compromise" in plan
    assert "trusted signing and protected release execution remain pending" in plan
    assert "factual panel execution and qualification remain pending" in plan
