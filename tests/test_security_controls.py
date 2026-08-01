import json
import re
from pathlib import Path


def test_security_control_manifest_is_bounded_and_complete() -> None:
    manifest = json.loads(Path("docs/security-control-manifest.json").read_text())
    assert manifest["status"] == "repository-baseline"
    assert {control["id"] for control in manifest["controls"]} == {"SC-01", "SC-02", "SC-03", "SC-04"}
    assert manifest["external_gates"]


def test_release_and_ci_actions_use_immutable_references() -> None:
    for path in Path(".github/workflows").glob("*.yml"):
        text = path.read_text()
        for use in re.findall(r"uses:\s*([^\s#]+)", text):
            assert "@" in use, f"unversioned action in {path}: {use}"
            ref = use.rsplit("@", 1)[1]
            if use.startswith(("actions/", "astral-sh/")):
                assert re.fullmatch(r"[0-9a-f]{40}", ref), f"mutable action ref in {path}: {use}"
