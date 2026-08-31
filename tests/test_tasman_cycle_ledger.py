from __future__ import annotations

import copy
import json
import runpy
from pathlib import Path
from unittest.mock import patch

import pytest

from riopa_provenance.hashing import sha256_bytes, sha256_json

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = runpy.run_path(str(ROOT / "scripts/tasman_cycle_ledger.py"))


@pytest.fixture
def bundle() -> dict:
    def doc(name: str) -> dict:
        return json.loads((ROOT / "docs" / name).read_bytes())

    return {
        "source": doc("tasman-publication-acceptance-20260830.json")["publication_receipt"],
        "derived": doc("tasman-derived-acceptance-20260831.json")["publication_receipt"],
        "provenance": doc("tasman-run-provenance-acceptance-20260831.json")["attempts"][0][
            "receipt"
        ],
        "comparison": doc("tasman-feature-comparison-acceptance-20260831.json")[
            "comparison_receipt"
        ],
    }


def encode(bundle: dict) -> tuple[dict, dict]:
    bundle = copy.deepcopy(bundle)
    for name in ("source", "derived"):
        digest = sha256_bytes(json.dumps(bundle[name]).encode())
        for target in ("provenance", "comparison"):
            bundle[target][name + "_receipt_sha256"] = digest
    bodies = {name: json.dumps(value).encode() for name, value in bundle.items()}
    return bodies, {name: sha256_bytes(body) for name, body in bodies.items()}


def append(bundle: dict, ledger: dict | None = None) -> dict:
    return SCRIPT["append_observation"](ledger, *encode(bundle))


def next_run(bundle: dict, day: int) -> dict:
    result = copy.deepcopy(bundle)
    p, s = result["provenance"], result["source"]
    run = str(40000000000 + day)
    p["cycle_key"] = s["source_run"] = run
    s["private_prefix"] = f"campaigns/{run}/tasman/1"
    for key in ("source_capture", "source_trigger", "publication"):
        record = p[key]
        record["run_id"] = run if key != "publication" else str(50000000000 + day)
        record["attempt"] = "1"
        record["event"] = "schedule" if key != "publication" else "workflow_run"
        for time in ("created_at", "run_started_at", "updated_at"):
            record[time] = f"2026-09-{day:02}T01:00:00Z"
    p["scheduled_source_trigger_observed"] = p["automatic_followup"] = True
    return result


def test_actual_metadata_manual_replay_deduplicates(bundle: dict) -> None:
    first = append(bundle)
    assert first["unique_source_run_count"] == 1
    assert first["events"][0]["manual_replay_ineligible"]
    assert first["scheduled_automatic_source_runs"] == []
    assert append(bundle, first) == first
    bundle["provenance"]["publication"]["attempt"] = "2"
    second = append(bundle, first)
    assert len(second["events"]) == 2
    assert second["unique_source_run_count"] == 1
    assert not second["three_cycle_gate_qualified"]


def test_three_synthetic_schedules_never_qualify(bundle: dict) -> None:
    ledger = None
    for day in range(1, 4):
        ledger = append(next_run(bundle, day), ledger)
    assert ledger["unique_source_run_count"] == 3
    assert len(ledger["scheduled_automatic_source_runs"]) == 3
    assert ledger["events"][2]["predecessor_source_run"] == "40000000002"
    assert not ledger["three_cycle_gate_qualified"]
    assert "adjacent-cycle" in ledger["qualification_gaps"][1]


@pytest.mark.parametrize("kind", ["hash", "conflict", "time", "tamper", "attempt"])
def test_fail_closed_and_recover_original(bundle: dict, kind: str) -> None:
    original = append(bundle)
    changed = copy.deepcopy(bundle)
    ledger = copy.deepcopy(original)
    if kind == "hash":
        bodies, hashes = encode(bundle)
        bodies["source"] += b" "
        with pytest.raises(ValueError):
            SCRIPT["append_observation"](ledger, bodies, hashes)
    else:
        if kind == "conflict":
            changed["provenance"]["source_capture"]["code_sha"] = "a" * 40
            changed["provenance"]["publication"]["attempt"] = "2"
        elif kind == "time":
            changed = next_run(bundle, 1)
            ledger = append(next_run(bundle, 2))
        elif kind == "tamper":
            ledger["events"][0]["manual_replay_ineligible"] = False
        else:
            changed["provenance"]["publication"]["code_sha"] = "a" * 40
        with pytest.raises(ValueError):
            append(changed, ledger)
    failed = SCRIPT["record_rejected_attempt"](original, "synthetic-failure", "ValueError")
    assert not failed["events"][-1]["hosted_recovery_qualified"]
    changed = copy.deepcopy(bundle)
    changed["provenance"]["publication"]["attempt"] = "2"
    recovered = append(changed, failed)
    assert len(recovered["events"]) == 3
    assert not recovered["three_cycle_gate_qualified"]
    assert append(bundle) == original


@pytest.mark.parametrize(
    "target,field,value",
    [
        ("source", "licence", "unknown"),
        ("source", "source_id", "wrong"),
        ("provenance", "repository", "wrong/repo"),
        ("provenance", "automatic_followup", True),
        ("comparison", "release_cycle_qualified", True),
        ("comparison", "baseline_role", "adjacent"),
        ("comparison", "derived_public_revision", "0" * 40),
    ],
)
def test_context_bindings(bundle: dict, target: str, field: str, value: object) -> None:
    bundle[target][field] = value
    with pytest.raises(ValueError):
        append(bundle)


def test_cli_fresh_bounded_output(bundle: dict, tmp_path: Path) -> None:
    bodies, hashes = encode(bundle)
    argv = ["ledger"]
    for name, body in bodies.items():
        path = tmp_path / name
        path.write_bytes(body)
        argv += [f"--{name}", str(path), f"--{name}-sha256", hashes[name]]
    output = tmp_path / "ledger.json"
    argv += ["--output", str(output)]
    with patch("sys.argv", argv):
        assert SCRIPT["main"]() == 0
        assert SCRIPT["main"]() == 1
    assert json.loads(output.read_bytes()) == append(bundle)


def test_invalid_paths_json_and_failure_redaction(tmp_path: Path) -> None:
    path = tmp_path / "evidence"
    path.write_bytes(b"{}")
    link = tmp_path / "link"
    link.symlink_to(path)
    with pytest.raises(ValueError):
        SCRIPT["read"](link)
    with pytest.raises(ValueError):
        SCRIPT["read"](path, 1)
    for data in (b'{"a":1,"a":2}', b'{"a":NaN}', b"[]"):
        with pytest.raises(ValueError):
            SCRIPT["parse"](data)
    with pytest.raises(ValueError):
        SCRIPT["record_rejected_attempt"](None, "test", "SECRET token")


def test_ledger_assessment_cannot_be_resealed_to_qualify(bundle: dict) -> None:
    ledger = append(bundle)
    ledger["three_cycle_gate_qualified"] = True
    ledger["ledger_sha256"] = sha256_json({k: v for k, v in ledger.items() if k != "ledger_sha256"})
    with pytest.raises(ValueError):
        SCRIPT["validate"](ledger)


def test_reversed_attempts_and_trigger_drift_rejected(bundle: dict) -> None:
    later = copy.deepcopy(bundle)
    later["provenance"]["publication"]["attempt"] = "2"
    ledger = append(later)
    with pytest.raises(ValueError):
        append(bundle, ledger)
    later["provenance"]["source_trigger"]["event"] = "schedule"
    later["provenance"]["scheduled_source_trigger_observed"] = True
    with pytest.raises(ValueError):
        append(later)


def test_resealed_eligibility_flag_rejected(bundle: dict) -> None:
    ledger = append(bundle)
    event = ledger["events"][0]
    event["scheduled_automatic_observation"] = True
    event["event_sha256"] = sha256_json({k: v for k, v in event.items() if k != "event_sha256"})
    with pytest.raises(ValueError):
        SCRIPT["assemble"](ledger["events"])
    bundle["comparison"]["source_run"] = "1"
    with pytest.raises(ValueError):
        append(bundle)
