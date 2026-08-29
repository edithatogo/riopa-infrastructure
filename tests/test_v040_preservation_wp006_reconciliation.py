import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(relative: str) -> dict[str, object]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_v040_preservation_receipts_close_only_the_preview_slice() -> None:
    record = _load("docs/v0.4.0-preservation-wp006-reconciliation-20260829.json")
    receipts = record["verified_receipts"]
    assert isinstance(receipts, list)
    assert {receipt["provider"] for receipt in receipts} == {"huggingface", "zenodo"}
    for receipt in receipts:
        path = ROOT / receipt["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == receipt["sha256"]

    wp006 = record["wp006"]
    assert wp006["status"] == "active"
    assert wp006["repository_owned_work"] == "partial"
    assert wp006["preservation_slice"] == "complete-for-v0.4.0-public-technical-preview"
    assert (
        "trusted signed conformance report bound to the eventual stable candidate"
        in wp006["remaining_acceptance"]
    )
    assert record["agent_panel_policy"]["other_human_required"] is False
    queue = _load("codex/implementation-queue.json")
    packages = queue["packages"]
    wp006_package = next(package for package in packages if package["id"] == "WP-006")
    assert wp006_package["title"] == (
        "Complete broader standards conformance and signed stable-candidate qualification"
    )
    assert len(wp006_package["acceptance"]) == 4
    assert any(
        "anonymously downloaded with byte verification" in item
        for item in wp006_package["acceptance"]
    )
    assert all("anonymously restored" not in item for item in wp006_package["acceptance"])

    evidence_id = record["evidence_id"]
    for track_id in (
        "interoperability_conformance_sdks_20260719",
        "methods_research_objects_20260718",
        "security_supply_chain_20260719",
        "publication_validation_20260718",
    ):
        metadata = _load(f"conductor/tracks/{track_id}/metadata.json")
        assert evidence_id in metadata["evidence"]


def test_active_metadata_no_longer_requires_external_people_or_stale_preview_receipts() -> None:
    forbidden = {
        "hf-zenodo-preservation-acceptance-receipts",
        "independent-external-reproduction",
        "independent-external-reproduction-pending",
        "external-reproduction-and-user-evidence",
    }
    for path in (ROOT / "conductor/tracks").glob("*/metadata.json"):
        metadata = json.loads(path.read_text(encoding="utf-8"))
        blockers = set(metadata.get("blocking_defects", []))
        assert not blockers.intersection(forbidden), path


def test_active_specs_use_subagent_clean_room_term() -> None:
    for path in (ROOT / "conductor/tracks").glob("*/spec.md"):
        text = path.read_text(encoding="utf-8")
        assert "external reproduction" not in text.lower(), path
