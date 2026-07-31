from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path
from types import SimpleNamespace

import pytest

from riopa_provenance import cli
from riopa_provenance.validation import ValidationResult


def test_validate_command_reports_success(capsys: pytest.CaptureFixture[str]) -> None:
    root = Path(__file__).resolve().parents[1]
    with pytest.raises(SystemExit) as exc:
        cli.main(["validate", "--root", str(root)])
    assert exc.value.code == 0
    output = capsys.readouterr().out
    assert "PASS" in output
    assert "0 failure(s)" in output


def test_validate_command_reports_failures(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    results = [
        ValidationResult(tmp_path / "valid.json", None, ()),
        ValidationResult(tmp_path / "invalid.json", None, ("broken", "also broken")),
    ]
    monkeypatch.setattr(cli, "validate_bundle", lambda _root: results)
    with pytest.raises(SystemExit) as exc:
        cli.main(["validate", "--root", str(tmp_path)])
    assert exc.value.code == 1
    output = capsys.readouterr().out
    assert "PASS" in output
    assert "FAIL" in output
    assert "broken" in output
    assert "1 failure(s)" in output


def test_methods_command_writes_output(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    output = tmp_path / "nested" / "METHODS.md"
    with pytest.raises(SystemExit) as exc:
        cli.main(
            [
                "methods",
                "--manifest",
                str(root / "examples/minimal/snapshot-manifest.json"),
                "--output",
                str(output),
            ]
        )
    assert exc.value.code == 0
    assert "Citable methods statement" in output.read_text(encoding="utf-8")
    assert "Methods written" in capsys.readouterr().out


def test_research_object_command_writes_output(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    root = Path(__file__).resolve().parents[1]
    output = tmp_path / "research-object"
    with pytest.raises(SystemExit) as exc:
        cli.main(
            [
                "research-object",
                "--manifest",
                str(root / "examples/minimal/snapshot-manifest.json"),
                "--output-dir",
                str(output),
            ]
        )
    assert exc.value.code == 0
    assert (output / "ro-crate-metadata.json").is_file()
    assert "Research object written" in capsys.readouterr().out


def test_roadmap_validate_command_reports_success(
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = Path(__file__).resolve().parents[1]
    with pytest.raises(SystemExit) as exc:
        cli.main(["roadmap", "validate", "--root", str(root)])
    assert exc.value.code == 0
    assert "PASS roadmap" in capsys.readouterr().out


def test_roadmap_status_json_reports_stable_target(
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = Path(__file__).resolve().parents[1]
    with pytest.raises(SystemExit) as exc:
        cli.main(
            [
                "roadmap",
                "status",
                "--root",
                str(root),
                "--release",
                "1.0.0",
                "--format",
                "json",
            ]
        )
    assert exc.value.code == 0
    payload = __import__("json").loads(capsys.readouterr().out)
    assert payload["stable_release"] == "1.0.0"
    assert payload["tracks"]["total"] == 28
    assert payload["releases"][0]["ready"] is False


def test_roadmap_generate_issues_command_writes_output(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    root = Path(__file__).resolve().parents[1]
    output = tmp_path / "issues.json"
    with pytest.raises(SystemExit) as exc:
        cli.main(
            [
                "roadmap",
                "generate-issues",
                "--root",
                str(root),
                "--output",
                str(output),
            ]
        )
    assert exc.value.code == 0
    payload = __import__("json").loads(output.read_text(encoding="utf-8"))
    assert len([item for item in payload["issues"] if item.get("parent") == "program-epic"]) == 28
    assert "Issue configuration written" in capsys.readouterr().out


def test_registry_endpoint_lookup_and_registered_auth(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry = {
        "sources": [
            {
                "source_id": "source",
                "endpoints": [{"endpoint_id": "endpoint", "url": "https://example.test/data"}],
            }
        ]
    }
    source, endpoint = cli._find_registry_endpoint(registry, "source", "endpoint")
    assert source["source_id"] == "source"
    assert cli._registered_auth(endpoint) == ("https://example.test/data", {}, {}, [])
    with pytest.raises(ValueError, match="source is not registered"):
        cli._find_registry_endpoint(registry, "missing", "endpoint")
    with pytest.raises(ValueError, match="endpoint is not registered"):
        cli._find_registry_endpoint(registry, "source", "missing")

    monkeypatch.setenv("RIOPA_TEST_KEY", "secret")
    base = {
        "url": "https://example.test/data",
        "authentication": {
            "type": "api-key",
            "environment_variable": "RIOPA_TEST_KEY",
        },
    }
    query = {**base, "authentication": {**base["authentication"], "secret_location": "query"}}
    assert cli._registered_auth(query)[1:] == ({"key": "secret"}, {}, ["secret"])
    header = {
        **base,
        "authentication": {
            **base["authentication"],
            "secret_location": "header",
            "credential_name": "Authorization",
        },
    }
    assert cli._registered_auth(header)[2] == {"Authorization": "secret"}
    path = {
        "url_template": "https://example.test/{token}/data",
        "authentication": {
            **base["authentication"],
            "secret_location": "path",
            "credential_name": "token",
        },
    }
    assert cli._registered_auth(path)[0] == "https://example.test/secret/data"


@pytest.mark.parametrize(
    ("endpoint", "message"),
    [
        ({"url": "x", "authentication": {"type": "oauth"}}, "does not support"),
        (
            {"url": "x", "authentication": {"type": "api-key"}},
            "no environment variable",
        ),
        (
            {
                "url": "x",
                "authentication": {
                    "type": "api-key",
                    "environment_variable": "UNSET_RIOPA_TEST_KEY",
                },
            },
            "is unset",
        ),
    ],
)
def test_registered_auth_rejects_invalid_configuration(
    endpoint: dict[str, object], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        cli._registered_auth(endpoint)


def test_registered_auth_rejects_invalid_secret_locations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("RIOPA_TEST_KEY", "secret")
    auth = {
        "type": "api-key",
        "environment_variable": "RIOPA_TEST_KEY",
        "secret_location": "path",
        "credential_name": "token",
    }
    with pytest.raises(ValueError, match="does not contain"):
        cli._registered_auth({"url": "https://example.test", "authentication": auth})
    with pytest.raises(ValueError, match="unsupported"):
        cli._registered_auth(
            {
                "url": "https://example.test",
                "authentication": {**auth, "secret_location": "cookie"},
            }
        )


def test_research_object_and_registry_validation_failure_handlers(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    invalid = SimpleNamespace(valid=False, root=tmp_path, path=tmp_path, errors=("bad",))
    monkeypatch.setattr(cli, "verify_research_object", lambda _root: invalid)
    assert cli._research_object_verify(Namespace(root=tmp_path)) == 1
    assert "FAIL research object" in capsys.readouterr().out
    monkeypatch.setattr(cli, "validate_registry", lambda _registry, _schema: invalid)
    assert cli._registry_validate(Namespace(registry="r", schema="s")) == 1
    assert "FAIL source registry" in capsys.readouterr().out


def test_spatial_geojson_handler_prints_materialization(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    product = SimpleNamespace(
        geoparquet_path=tmp_path / "x.parquet",
        duckdb_path=tmp_path / "x.duckdb",
        quality_report_path=tmp_path / "x.json",
        feature_count=2,
        geoparquet_sha256="a" * 64,
        duckdb_sha256="b" * 64,
    )
    import riopa_provenance.spatial

    monkeypatch.setattr(
        riopa_provenance.spatial, "materialize_geojson", lambda *args, **kwargs: product
    )
    result = cli._spatial_geojson(
        Namespace(
            input="input",
            output_dir="output",
            source_id="source",
            layer_id="layer",
            capture_id="capture",
            crs=None,
            object_id_field=None,
            base_name="base",
        )
    )
    assert result == 0
    assert json.loads(capsys.readouterr().out)["feature_count"] == 2


def test_roadmap_failure_status_file_and_main_error(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(cli, "validate_roadmap", lambda *args, **kwargs: ["one", "two"])
    assert cli._roadmap_validate(Namespace(root=tmp_path, skip_issue_drift=True)) == 1
    assert "2 problem(s)" in capsys.readouterr().out

    monkeypatch.setattr(cli, "roadmap_status", lambda *_args: {"ready": False})
    monkeypatch.setattr(cli, "render_status_markdown", lambda _status: "# Status\n")
    output = tmp_path / "nested" / "status.md"
    assert (
        cli._roadmap_status(
            Namespace(root=tmp_path, release=None, format="markdown", output=output)
        )
        == 0
    )
    assert output.read_text(encoding="utf-8") == "# Status\n"

    monkeypatch.setattr(
        cli,
        "validate_bundle",
        lambda _root: (_ for _ in ()).throw(ValueError("bad")),
    )
    with pytest.raises(SystemExit) as exc:
        cli.main(["validate", "--root", str(tmp_path)])
    assert exc.value.code == 1
    assert "ERROR bad" in capsys.readouterr().err
