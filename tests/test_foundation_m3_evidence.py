import json
import shutil
from pathlib import Path

import pytest

from scripts.validate_foundation_m3_evidence import CANDIDATE, MIGRATIONS, PAIR, build_evidence

ROOT = Path(__file__).resolve().parents[1]


def copy_inputs(tmp_path: Path) -> Path:
    shutil.copytree(ROOT / "evidence", tmp_path / "evidence")
    for relative in (CANDIDATE, PAIR, *MIGRATIONS):
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    return tmp_path


def test_packet_rebuilds_without_promoting_fixture_evidence() -> None:
    packet = build_evidence(ROOT)
    assert packet == json.loads((ROOT / "docs/foundation-m3-evidence-20260912.json").read_text())
    assert packet["promotion_allowed"] is False
    assert len(packet["remaining_m3_gates"]) == 3
    assert len(packet["outputs"]) == 3
    assert all("execution-unverified" in item["status"] for item in packet["migrations"])


@pytest.mark.parametrize(
    "relative",
    [
        "evidence/stats-nz-meshblock-2026-projection/capture-records.jsonl",
        "evidence/stats-nz-meshblock-2026-projection/materialization-receipt.json",
        "evidence/wp007-real-slice/materialized/wcc-zone-objectid-1.parquet",
    ],
)
def test_input_or_output_drift_is_rejected(tmp_path: Path, relative: str) -> None:
    root = copy_inputs(tmp_path)
    path = root / relative
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(ValueError):
        build_evidence(root)


def test_invalid_migration_cannot_be_reported_as_valid(tmp_path: Path) -> None:
    root = copy_inputs(tmp_path)
    path = root / MIGRATIONS[0]
    fixture = json.loads(path.read_text())
    fixture["to_version"] = fixture["from_version"]
    path.write_text(json.dumps(fixture))
    with pytest.raises(ValueError, match="version"):
        build_evidence(root)


def test_historical_receipt_is_not_silently_rebased(tmp_path: Path) -> None:
    root = copy_inputs(tmp_path)
    path = root / PAIR
    packet = json.loads(path.read_text())
    key = "evidence/stats-nz-meshblock-2026-projection/records-manifest.json"
    packet["file_sha256"][key] = "0" * 64
    path.write_text(json.dumps(packet))
    with pytest.raises(ValueError, match="historical"):
        build_evidence(root)
