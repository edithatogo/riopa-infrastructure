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
                if (
                    path.name,
                    job_name,
                ) in {
                    ("release.yml", "publish"),
                    ("v020-release-recovery.yml", "publish"),
                } and value == "write":
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


def test_research_object_attestation_contract_matches_release_workflow() -> None:
    contract = json.loads(
        Path("docs/research-object-attestation-contract-20260825.json").read_text()
    )
    workflow = Path(".github/workflows/release.yml").read_text()
    assert contract["status"] == "repository-workflow-ready-hosted-execution-pending"
    assert contract["workflow"] == ".github/workflows/release.yml"
    assert "scripts/build_sbom.sh" in workflow
    assert "actions/attest@" in workflow
    assert "gh attestation verify" in workflow
    assert "SHA256SUMS" in workflow
    assert contract["non_claims"]


def test_github_security_observation_is_fail_closed() -> None:
    observation = json.loads(Path("docs/github-security-observation-20260825.json").read_text())
    endpoints = observation["endpoints"]
    assert observation["status"] == "observation-only"
    assert endpoints["secret_scanning_alerts"]["open_alert_count"] == 0
    assert endpoints["code_scanning_alerts"]["open_alert_count"] == 0
    assert endpoints["dependabot_alerts"]["alert_count"] >= 0
    assert observation["non_claims"]


def test_dependabot_remediation_receipt_binds_fixed_alerts_to_lockfile() -> None:
    receipt = json.loads(Path("docs/github-dependabot-remediation-20260825.json").read_text())
    assert receipt["status"] == "fixed-alerts-verified-in-lockfile"
    assert receipt["manifest"] == "uv.lock"
    assert {(item["package"], item["locked_version"]) for item in receipt["alerts"]} == {
        ("cryptography", "50.0.0"),
        ("pytest", "9.1.1"),
    }
    assert all(item["state"] == "fixed" for item in receipt["alerts"])
    assert receipt["non_claims"]
