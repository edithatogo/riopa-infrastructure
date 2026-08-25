from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "rust" / "riopa-conformance" / "Cargo.toml"


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
