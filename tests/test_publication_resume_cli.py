from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from riopa_provenance import cli
from riopa_provenance.hashing import sha256_json
from riopa_provenance.publication import (
    build_publication_resume_plan,
    initialise_publication_state,
    record_publication_receipt,
)


@pytest.fixture
def inputs(tmp_path: Path) -> dict[str, Any]:
    plan = {
        "publication_id": "urn:riopa:publication:cli-test",
        "status": "ready",
        "targets": [{"target_id": name} for name in ("zenodo", "github", "hugging-face")],
    }
    plan["plan_sha256"] = sha256_json(plan)
    state = initialise_publication_state(plan)
    receipts = [
        {
            "target_id": name,
            "operation_key": entry["operation_key"],
            "plan_sha256": plan["plan_sha256"],
            "identifier": f"https://example.test/{name}",
            "revision": "opaque-provider-revision",
            "recorded_at": "2026-08-31T00:00:00Z",
        }
        for name, entry in state["targets"].items()
    ]
    values = {"plan": plan, "state": state, "receipts": receipts}
    paths = {}
    for name, value in values.items():
        paths[name] = tmp_path / f"{name}.json"
        paths[name].write_text(json.dumps(value))
    return {"values": values, "paths": paths}


def invoke(inputs: dict, capsys, *, receipts: bool = True, extra: list[str] | None = None):
    paths = inputs["paths"]
    argv = ["publication", "resume", "--plan", str(paths["plan"]), "--state", str(paths["state"])]
    if receipts:
        argv += ["--receipts", str(paths["receipts"])]
    argv += extra or []
    before = {p: p.read_bytes() for p in paths.values() if p.is_file()}
    with pytest.raises(SystemExit) as error:
        cli.main(argv)
    captured = capsys.readouterr()
    assert all(p.read_bytes() == body for p, body in before.items())
    return error.value.code, captured


def test_resume_json_stdout_three_providers_is_read_only(inputs: dict, capsys) -> None:
    files_before = sorted(inputs["paths"]["plan"].parent.iterdir())
    code, captured = invoke(inputs, capsys)
    assert code == 0 and captured.err == ""
    result = json.loads(captured.out)
    assert captured.out == json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    assert result == build_publication_resume_plan(**inputs["values"])
    assert result["reconciled_state"]["status"] == "published"
    assert [t["target_id"] for t in result["targets"]] == ["github", "hugging-face", "zenodo"]
    assert all(t["remote_write_authorized"] is False for t in result["targets"])
    assert result["remote_write_authorized"] is False
    assert sorted(inputs["paths"]["plan"].parent.iterdir()) == files_before


def test_optional_partial_replay_and_receipt_order(inputs: dict, capsys) -> None:
    code, captured = invoke(inputs, capsys, receipts=False)
    assert code == 0
    assert all(
        t["disposition"] == "provider-reconciliation-required"
        for t in json.loads(captured.out)["targets"]
    )
    receipts = inputs["values"]["receipts"]
    inputs["paths"]["receipts"].write_text(json.dumps(receipts[:1]))
    code, captured = invoke(inputs, capsys)
    assert code == 0
    partial = json.loads(captured.out)["reconciled_state"]
    assert partial["status"] == "in-progress"
    inputs["paths"]["state"].write_text(json.dumps(partial))
    inputs["paths"]["receipts"].write_text(json.dumps(receipts))
    code, captured = invoke(inputs, capsys)
    assert code == 0
    first = captured.out
    inputs["paths"]["receipts"].write_text(json.dumps(list(reversed(receipts))))
    code, captured = invoke(inputs, capsys)
    assert code == 0 and captured.out == first
    complete = json.loads(first)["reconciled_state"]
    inputs["paths"]["state"].write_text(json.dumps(complete))
    code, captured = invoke(inputs, capsys)
    assert code == 0 and json.loads(captured.out)["reconciled_state"] == complete


@pytest.mark.parametrize("fault", ["plan-mismatch", "target-mismatch", "conflict"])
def test_binding_failures_have_no_stdout_or_mutation(inputs: dict, capsys, fault: str) -> None:
    state = inputs["values"]["state"]
    if fault == "plan-mismatch":
        state["publication_id"] = "SECRET-private-publication"
    elif fault == "target-mismatch":
        del state["targets"]["zenodo"]
    else:
        state = record_publication_receipt(state, inputs["values"]["receipts"][0])
        inputs["values"]["receipts"][0]["revision"] = "SECRET-conflicting-revision"
        inputs["paths"]["receipts"].write_text(json.dumps(inputs["values"]["receipts"]))
    state["state_sha256"] = sha256_json(state, omit_keys={"state_sha256"})
    inputs["paths"]["state"].write_text(json.dumps(state))
    code, captured = invoke(inputs, capsys, receipts=fault == "conflict")
    assert code == 1 and captured.out == ""
    assert captured.err == "ERROR publication resume: invalid recovery input or evidence binding\n"
    assert "SECRET" not in captured.err


@pytest.mark.parametrize(
    "name,body",
    [
        ("plan", b"[]"),
        ("state", b"null"),
        ("receipts", b"{}"),
        ("receipts", b"false"),
        ("receipts", b"[1]"),
        ("plan", b"{SECRET broken"),
        ("state", b"\xff"),
        ("state", b""),
        ("plan", b'{"x":NaN}'),
        ("plan", b'{"x":Infinity}'),
        ("receipts", b"[-Infinity]"),
    ],
)
def test_invalid_json_shapes_and_constants_fail_concisely(
    inputs: dict, capsys, name: str, body: bytes
) -> None:
    inputs["paths"][name].write_bytes(body)
    code, captured = invoke(inputs, capsys)
    assert code == 1 and captured.out == ""
    assert "invalid recovery input" in captured.err
    assert "SECRET" not in captured.err


@pytest.mark.parametrize(
    "name,key",
    [
        ("plan", "status"),
        ("plan", "target_id"),
        ("state", "operation_key"),
        ("receipts", "identifier"),
    ],
)
def test_duplicate_keys_rejected_even_when_last_value_would_validate(
    inputs: dict, capsys, name: str, key: str
) -> None:
    path = inputs["paths"][name]
    text = path.read_text()
    text = text.replace(f'"{key}":', f'"{key}": "SECRET-duplicate", "{key}":', 1)
    path.write_text(text)
    code, captured = invoke(inputs, capsys)
    assert code == 1 and captured.out == ""
    assert "SECRET" not in captured.err and key not in captured.err


@pytest.mark.parametrize("fault", ["missing", "directory", "oversized", "empty-receipts-path"])
def test_missing_or_unbounded_files_fail_without_output(inputs: dict, capsys, fault: str) -> None:
    if fault == "missing":
        inputs["paths"]["plan"] = inputs["paths"]["plan"].with_name("SECRET-missing.json")
    elif fault == "directory":
        inputs["paths"]["plan"] = inputs["paths"]["plan"].parent
    elif fault == "oversized":
        inputs["paths"]["plan"].write_bytes(b" " * (8 * 1024 * 1024 + 1))
    code, captured = invoke(
        inputs, capsys, extra=["--receipts", ""] if fault == "empty-receipts-path" else None
    )
    assert code == 1 and captured.out == ""
    assert "SECRET" not in captured.err


def test_resume_has_no_output_file_option(inputs: dict, capsys) -> None:
    output = inputs["paths"]["plan"].with_name("must-not-exist.json")
    code, captured = invoke(inputs, capsys, extra=["--output", str(output)])
    assert code == 2 and captured.out == ""
    assert not output.exists()


def test_resume_requires_plan_and_state(capsys) -> None:
    with pytest.raises(SystemExit) as error:
        cli.main(["publication", "resume"])
    assert error.value.code == 2
    captured = capsys.readouterr()
    assert captured.out == "" and "required" in captured.err


def test_reordered_object_keys_produce_identical_stdout(inputs: dict, capsys) -> None:
    code, original = invoke(inputs, capsys)
    assert code == 0
    for path in inputs["paths"].values():
        value = json.loads(path.read_bytes())
        path.write_text(json.dumps(value, sort_keys=True))
    code, reordered = invoke(inputs, capsys)
    assert code == 0 and reordered.out == original.out
