import copy
import json
import subprocess
from pathlib import Path

from riopa_provenance.capture_migration import migrate_capture, recover_capture
from riopa_provenance.hashing import sha256_json

SOURCE = Path("evidence/stats-nz-meshblock-2026-projection/capture-records.jsonl")


def run_node(requests):
    return json.loads(
        subprocess.run(
            ["node", "scripts/capture_migration_node.mjs"],
            input=json.dumps(requests),
            text=True,
            capture_output=True,
            check=True,
        ).stdout
    )


def bind(record):
    digest = sha256_json(record)
    return {
        "record": record,
        "record_sha256": digest,
        "capture_id": f"urn:riopa:capture:sha256:{digest}",
    }


def test_all_archived_captures_migrate_and_recover_across_runtimes():
    sources = [json.loads(line) for line in SOURCE.read_text().splitlines()]
    python_views = [migrate_capture(source) for source in sources]
    node_views = run_node([{"operation": "migrate", "value": source} for source in sources])
    assert node_views == [{"accepted": True, "value": view} for view in python_views]
    assert [recover_capture(result["value"]) for result in node_views] == sources
    assert run_node([{"operation": "recover", "value": view} for view in python_views]) == [
        {"accepted": True, "value": source} for source in sources
    ]


def test_extension_unicode_number_and_facet_roundtrip():
    source = json.loads(SOURCE.read_text().splitlines()[0])
    source["record"]["extension"] = {
        "😀": [1e-7, -0.0, 1.5, 1e20, 1e21, "Māori"],
        "\ue000": {"view_sha256": "nested preserved"},
    }
    source = bind(source["record"])
    facets = {"quality": [{"uri": "urn:test:quality", "sha256": "a" * 64}]}
    view = migrate_capture(source, facets=facets)
    assert run_node(
        [
            {"operation": "migrate", "value": source, "facets": facets},
            {"operation": "recover", "value": view},
        ]
    ) == [{"accepted": True, "value": view}, {"accepted": True, "value": source}]


def test_negative_contracts_have_python_node_parity():
    source = json.loads(SOURCE.read_text().splitlines()[0])
    view = migrate_capture(source)
    requests = []
    for field, value in [
        ("schema_version", "9"),
        ("record_type", "other"),
        ("source_id", "\x1c\x85"),
    ]:
        changed = copy.deepcopy(source["record"])
        changed[field] = value
        requests.append({"operation": "migrate", "value": bind(changed)})
    for field in ["capture_id", "record_sha256"]:
        changed = copy.deepcopy(source)
        changed[field] = "0" * 64
        requests.append({"operation": "migrate", "value": changed})
    for facets in [
        {"other": []},
        {"quality": []},
        {"quality": [{"uri": "\x1c", "sha256": "a" * 64}]},
        {"quality": [{"uri": "urn:test", "sha256": "A" * 64}]},
        {"quality": [{"uri": "urn:test", "sha256": "a" * 64 + "\n"}]},
    ]:
        requests.append({"operation": "migrate", "value": source, "facets": facets})
    for field, value in [
        ("schema_version", "9"),
        ("view_sha256", "a" * 64),
        ("source", []),
        ("facets", []),
        ("extra", "discard"),
    ]:
        changed = copy.deepcopy(view)
        changed[field] = value
        requests.append({"operation": "recover", "value": changed})
    for request in requests:
        try:
            if request["operation"] == "migrate":
                migrate_capture(request["value"], facets=request.get("facets"))
            else:
                recover_capture(request["value"])
        except ValueError:
            pass
        else:
            raise AssertionError("Python accepted a negative fixture")
    assert run_node(requests) == [{"accepted": False}] * len(requests)


def test_recorded_cross_runtime_evidence_reproduces():
    from scripts.build_capture_parity_evidence import build_evidence

    assert build_evidence(Path(".")) == json.loads(
        Path("docs/archived-capture-parity-evidence-20260912.json").read_text()
    )
