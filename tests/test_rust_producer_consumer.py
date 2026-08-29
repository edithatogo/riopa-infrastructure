from __future__ import annotations

import json
import subprocess
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "rust" / "riopa-conformance" / "Cargo.toml"
CLIENT_FIXTURE = ROOT / "conformance" / "v1" / "client-workflow.json"


def run_exchange(mode: str, *, stdin: str | None = None) -> str:
    result = subprocess.run(
        [
            "cargo",
            "run",
            "--quiet",
            "--locked",
            "--manifest-path",
            str(MANIFEST),
            "--bin",
            "conformance_exchange",
            "--",
            mode,
        ],
        cwd=ROOT,
        input=stdin,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip()


def run_corpus_hashes() -> list[tuple[str, str]]:
    result = subprocess.run(
        [
            "cargo",
            "run",
            "--quiet",
            "--locked",
            "--manifest-path",
            str(MANIFEST),
            "--bin",
            "conformance_corpus",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [tuple(line.split("\t", maxsplit=1)) for line in result.stdout.splitlines()]


def run_client_workflow(path: Path, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "cargo",
            "run",
            "--quiet",
            "--locked",
            "--manifest-path",
            str(MANIFEST),
            "--bin",
            "client_workflow",
            "--",
            str(path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=check,
    )


def test_rust_producer_python_consumer_and_python_producer_rust_consumer() -> None:
    rust_wire = run_exchange("produce")
    fields = rust_wire.split("\t")
    assert fields == [
        "urn:riopa:mapping:exchange",
        "source:fixture",
        "urn:riopa:concept:example",
        "medium",
        "fixture:exchange",
    ]

    python_wire = "\t".join(
        [
            "urn:riopa:mapping:python",
            "source:python-fixture",
            "urn:riopa:concept:example",
            "high",
            "fixture:python",
        ]
    )
    assert run_exchange("consume", stdin=python_wire + "\n") == python_wire


def test_rust_canonical_hashes_match_the_conformance_corpus() -> None:
    corpus = json.loads((ROOT / "conformance/v1/corpus.json").read_text(encoding="utf-8"))
    expected = [(case["case_id"], case["expected_sha256"]) for case in corpus["cases"]]
    assert run_corpus_hashes() == expected


def test_separately_implemented_rust_client_completes_workflow() -> None:
    report = json.loads(run_client_workflow(CLIENT_FIXTURE).stdout)
    fixture = json.loads(CLIENT_FIXTURE.read_text(encoding="utf-8"))
    assert report == {
        "contract_version": "1.0.0",
        "capture_id": fixture["capture"]["capture_id"],
        "capture_sha256": fixture["capture"]["expected_sha256"],
        "capture_status": "passed",
        "validation_status": "passed",
        "lineage_status": "passed",
        "lineage": sorted(fixture["expected_lineage"]),
    }


def test_rust_client_fails_closed_on_digest_and_lineage_drift(tmp_path: Path) -> None:
    fixture = json.loads(CLIENT_FIXTURE.read_text(encoding="utf-8"))
    fixture["capture"]["payload"]["status"] = "tampered"
    path = tmp_path / "bad-digest.json"
    path.write_text(json.dumps(fixture), encoding="utf-8")
    result = run_client_workflow(path, check=False)
    assert result.returncode == 1
    assert "capture payload digest mismatch" in result.stderr

    fixture = json.loads(CLIENT_FIXTURE.read_text(encoding="utf-8"))
    fixture["expected_lineage"].append("urn:riopa:missing")
    path = tmp_path / "bad-lineage.json"
    path.write_text(json.dumps(fixture), encoding="utf-8")
    result = run_client_workflow(path, check=False)
    assert result.returncode == 1
    assert "lineage query result mismatch" in result.stderr


def test_rust_client_fails_closed_on_contract_and_required_field_drift(
    tmp_path: Path,
) -> None:
    original = json.loads(CLIENT_FIXTURE.read_text(encoding="utf-8"))
    mutations = [
        ("workflow-version", lambda item: item.update(contract_version="2.0.0")),
        (
            "query-version",
            lambda item: item["lineage_query"].update(contract_version="2.0.0"),
        ),
        (
            "required-field",
            lambda item: item["validation"]["required_fields"].append("missing_field"),
        ),
    ]
    for name, mutate in mutations:
        fixture = deepcopy(original)
        mutate(fixture)
        path = tmp_path / f"{name}.json"
        path.write_text(json.dumps(fixture), encoding="utf-8")
        result = run_client_workflow(path, check=False)
        assert result.returncode == 1
        assert "client workflow failed" in result.stderr
