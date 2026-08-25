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


def test_lineage_export_prov_jsonld_command_writes_output(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    root = Path(__file__).resolve().parents[1]
    database = tmp_path / "lineage.sqlite"
    output = tmp_path / "prov.jsonld"
    index = cli.LineageIndex(database)
    index.import_manifest(
        root / "examples/minimal/snapshot-manifest.json", schema_dir=root / "schemas"
    )
    with pytest.raises(SystemExit) as exc:
        cli.main(
            [
                "lineage",
                "export-prov-jsonld",
                "--database",
                str(database),
                "--output",
                str(output),
            ]
        )
    assert exc.value.code == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["riopa:promotionAllowed"] is False
    assert "PROV JSON-LD projection written" in capsys.readouterr().out


def test_lineage_nodes_command_reports_page(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = Path(__file__).resolve().parents[1]
    database = tmp_path / "lineage.sqlite"
    index = cli.LineageIndex(database)
    index.import_manifest(
        root / "examples/minimal/snapshot-manifest.json", schema_dir=root / "schemas"
    )
    with pytest.raises(SystemExit) as exc:
        cli.main(["lineage", "nodes", "--database", str(database), "--limit", "1"])
    assert exc.value.code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["pagination"]["total"] >= 1
    assert len(payload["nodes"]) == 1


def test_lineage_query_command_reports_bounded_answer(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = Path(__file__).resolve().parents[1]
    database = tmp_path / "lineage.sqlite"
    index = cli.LineageIndex(database)
    index.import_manifest(
        root / "examples/minimal/snapshot-manifest.json", schema_dir=root / "schemas"
    )
    with pytest.raises(SystemExit) as exc:
        cli.main(
            [
                "lineage",
                "query",
                "--database",
                str(database),
                "--node-id",
                "urn:riopa:snapshot:nz-spatial-example:2026.07.18:example",
                "--question",
                "where",
                "--page-size",
                "1",
            ]
        )
    assert exc.value.code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["question"] == "where"
    assert payload["cache"]["hit"] is False
    assert payload["pagination"]["limit"] == 1
    assert payload["projection"]["freshness"] == "current-for-listed-authoritative-evidence"


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
    assert payload["tracks"]["total"] == 29
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


def test_success_validation_and_registry_handlers(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    valid = SimpleNamespace(valid=True, root=tmp_path, path=tmp_path, errors=())
    monkeypatch.setattr(cli, "verify_research_object", lambda _root: valid)
    assert cli._research_object_verify(Namespace(root=tmp_path)) == 0
    assert "PASS research object" in capsys.readouterr().out

    monkeypatch.setattr(cli, "validate_registry", lambda _registry, _schema: valid)
    assert cli._registry_validate(Namespace(registry="registry", schema="schema")) == 0
    assert "PASS source registry" in capsys.readouterr().out

    registry = {"registry_version": "1.0", "sources": []}
    monkeypatch.setattr(cli, "import_district_plans_csv", lambda *args, **kwargs: registry)
    monkeypatch.setattr(
        cli,
        "write_registry_json",
        lambda value, output: (
            Path(output).write_text(json.dumps(value), encoding="utf-8") or Path(output)
        ),
    )
    output = tmp_path / "registry.json"
    assert (
        cli._registry_import(
            Namespace(
                csv="plans.csv",
                generated_at="2026-07-31T00:00:00Z",
                catalogue_url="https://district-plans.nz/",
                output=output,
            )
        )
        == 0
    )
    assert json.loads(output.read_text(encoding="utf-8")) == registry
    assert "Source registry written" in capsys.readouterr().out


def _network_args(tmp_path: Path, **overrides: object) -> Namespace:
    values: dict[str, object] = {
        "registry": "registry.json",
        "schema": "schema.json",
        "source_id": "source",
        "endpoint_id": "endpoint",
        "store": tmp_path / "captures",
        "capture_store": tmp_path / "captures",
        "max_response_bytes": 1024,
        "connect_timeout": 1.0,
        "read_timeout": 2.0,
        "trust_environment": False,
        "max_pages": 3,
        "where": "1=1",
        "out_fields": "*",
        "layer_id": None,
        "type_name": "ns:zones",
        "page_size": 10,
        "sort_by": "id",
        "id_property": "id",
        "srs_name": None,
        "cql_filter": None,
    }
    values.update(overrides)
    return Namespace(**values)


class _FakeHttpClient:
    closed = False

    def __init__(self, **_kwargs: object) -> None:
        pass

    def __enter__(self) -> _FakeHttpClient:
        return self

    def __exit__(self, *_args: object) -> None:
        self.closed = True

    def close(self) -> None:
        self.closed = True


def test_archive_handlers_capture_registered_sources(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    import httpx

    import riopa_provenance.arcgis as arcgis
    import riopa_provenance.capture as capture
    import riopa_provenance.wfs as wfs

    valid = SimpleNamespace(valid=True, errors=())
    monkeypatch.setattr(cli, "validate_registry", lambda *_args: valid)
    endpoints = {
        "arcgis": {
            "endpoint_id": "endpoint",
            "enabled": True,
            "mechanism": "arcgis-feature-service",
            "url": "https://example.test/FeatureServer",
            "layer_ids": [4],
        },
        "wfs": {
            "endpoint_id": "endpoint",
            "enabled": True,
            "mechanism": "wfs",
            "url": "https://example.test/wfs",
            "expected_crs": "EPSG:2193",
        },
        "resource": {
            "endpoint_id": "endpoint",
            "enabled": True,
            "capture_strategy": "download-whole",
            "url": "https://example.test/data.csv",
        },
    }
    selected = endpoints["arcgis"]
    monkeypatch.setattr(
        cli,
        "load_registry",
        lambda _path: {"sources": [{"source_id": "source", "endpoints": [selected]}]},
    )
    monkeypatch.setattr(httpx, "Client", _FakeHttpClient)
    monkeypatch.setattr(capture, "CaptureStore", lambda path: path)
    monkeypatch.setattr(capture, "CapturePolicy", lambda **kwargs: kwargs)

    arcgis_result = SimpleNamespace(
        capture_set_id="arcgis-set",
        source_id="source",
        service_url="https://example.test/FeatureServer",
        layer_id=4,
        feature_count=2,
        page_captures=("one",),
        manifest_path=tmp_path / "arcgis.json",
    )

    class FakeArcGIS:
        def __init__(self, _client: object, max_pages: int) -> None:
            assert max_pages == 3

        def archive_layer(self, **kwargs: object) -> object:
            assert kwargs["layer_id"] == 4
            return arcgis_result

    monkeypatch.setattr(arcgis, "ArcGISFeatureLayerArchiver", FakeArcGIS)
    assert cli._archive_arcgis(_network_args(tmp_path)) == 0
    assert json.loads(capsys.readouterr().out)["capture_count"] == 2

    selected = endpoints["wfs"]
    wfs_result = SimpleNamespace(
        capture_set_id="wfs-set",
        source_id="source",
        service_url="https://example.test/wfs",
        type_name="ns:zones",
        feature_count=3,
        page_captures=("one", "two"),
        manifest_path=tmp_path / "wfs.json",
    )

    class FakeWFS:
        def __init__(self, _client: object, max_pages: int) -> None:
            assert max_pages == 3

        def archive_feature_type(self, **kwargs: object) -> object:
            assert kwargs["srs_name"] == "EPSG:2193"
            return wfs_result

    monkeypatch.setattr(wfs, "WFSFeatureTypeArchiver", FakeWFS)
    assert cli._archive_wfs(_network_args(tmp_path)) == 0
    assert json.loads(capsys.readouterr().out)["capture_count"] == 4

    selected = endpoints["resource"]
    resource_result = SimpleNamespace(
        capture_id="capture",
        source_id="source",
        endpoint_id="endpoint",
        status_code=200,
        object_sha256="a" * 64,
        size_bytes=12,
        object_path=tmp_path / "object",
        metadata_path=tmp_path / "metadata.json",
    )

    class FakeCaptureClient:
        def __init__(self, **_kwargs: object) -> None:
            pass

        def capture(self, method: str, url: str, **_kwargs: object) -> object:
            assert (method, url) == ("GET", "https://example.test/data.csv")
            return resource_result

    monkeypatch.setattr(capture, "HttpCaptureClient", FakeCaptureClient)
    assert cli._archive_resource(_network_args(tmp_path)) == 0
    assert json.loads(capsys.readouterr().out)["status_code"] == 200


@pytest.mark.parametrize(
    ("handler", "endpoint", "message"),
    [
        (
            cli._archive_arcgis,
            {"enabled": False, "mechanism": "arcgis-feature-service"},
            "disabled",
        ),
        (
            cli._archive_arcgis,
            {"enabled": True, "mechanism": "wfs", "url": "https://example.test"},
            "not an ArcGIS",
        ),
        (
            cli._archive_wfs,
            {"enabled": True, "mechanism": "arcgis-feature-service", "url": "https://example.test"},
            "not WFS",
        ),
        (
            cli._archive_resource,
            {
                "enabled": True,
                "capture_strategy": "paginated",
                "url": "https://example.test",
            },
            "whole-resource",
        ),
    ],
)
def test_archive_handlers_reject_registry_mismatch(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    handler: object,
    endpoint: dict[str, object],
    message: str,
) -> None:
    monkeypatch.setattr(cli, "validate_registry", lambda *_args: SimpleNamespace(valid=True))
    monkeypatch.setattr(
        cli,
        "load_registry",
        lambda _path: {
            "sources": [
                {
                    "source_id": "source",
                    "endpoints": [{"endpoint_id": "endpoint", **endpoint}],
                }
            ]
        },
    )
    with pytest.raises(ValueError, match=message):
        handler(_network_args(tmp_path))


def test_arcgis_layer_selection_and_registry_validation_errors(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        cli,
        "validate_registry",
        lambda *_args: SimpleNamespace(valid=False, errors=("bad schema",)),
    )
    with pytest.raises(ValueError, match="bad schema"):
        cli._archive_arcgis(_network_args(tmp_path))

    monkeypatch.setattr(cli, "validate_registry", lambda *_args: SimpleNamespace(valid=True))
    endpoint = {
        "endpoint_id": "endpoint",
        "enabled": True,
        "mechanism": "arcgis-map-service",
        "url": "https://example.test/MapServer",
        "layer_ids": [1, 2],
    }
    monkeypatch.setattr(
        cli,
        "load_registry",
        lambda _path: {"sources": [{"source_id": "source", "endpoints": [endpoint]}]},
    )
    with pytest.raises(ValueError, match="--layer-id is required"):
        cli._archive_arcgis(_network_args(tmp_path))
    with pytest.raises(ValueError, match="not declared"):
        cli._archive_arcgis(_network_args(tmp_path, layer_id=3))


def test_spatial_lineage_and_publication_handlers(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    import riopa_provenance.spatial as spatial

    product = SimpleNamespace(
        geoparquet_path=tmp_path / "x.parquet",
        duckdb_path=tmp_path / "x.duckdb",
        quality_report_path=tmp_path / "quality.json",
        feature_count=5,
        geoparquet_sha256="a" * 64,
        duckdb_sha256="b" * 64,
    )
    monkeypatch.setattr(spatial, "materialize_arcgis_capture_set", lambda *args, **kwargs: product)
    monkeypatch.setattr(spatial, "materialize_wfs_capture_set", lambda *args, **kwargs: product)
    common = Namespace(
        capture_set="set.json",
        store=tmp_path,
        output_dir=tmp_path,
        crs=None,
        base_name="zones",
        canonical_layer_id="canonical",
    )
    assert cli._spatial_arcgis(common) == 0
    assert json.loads(capsys.readouterr().out)["feature_count"] == 5
    assert cli._spatial_wfs(common) == 0
    assert json.loads(capsys.readouterr().out)["geoparquet_sha256"] == "a" * 64

    class FakeLineage:
        path = tmp_path / "lineage.duckdb"

        def __init__(self, _database: object) -> None:
            pass

        def import_manifest(self, _manifest: object, *, schema_dir: object) -> str:
            assert schema_dir == "schemas"
            return "snapshot"

        def upstream(self, node_id: str, *, max_depth: int) -> list[str]:
            return [node_id, f"depth-{max_depth}"]

        def downstream(self, node_id: str, *, max_depth: int) -> list[str]:
            return [f"{node_id}-child", f"depth-{max_depth}"]

        def rebuild_impact(self, node_id: object, *, max_depth: int) -> dict[str, object]:
            return {"nodes": node_id, "max_depth": max_depth}

    monkeypatch.setattr(cli, "LineageIndex", FakeLineage)
    assert (
        cli._lineage_build(Namespace(database="db", manifest="manifest", schema_dir="schemas")) == 0
    )
    assert "snapshot" in capsys.readouterr().out
    for direction in ("upstream", "downstream"):
        assert (
            cli._lineage_walk(
                Namespace(database="db", node_id="node", direction=direction, max_depth=2)
            )
            == 0
        )
        assert json.loads(capsys.readouterr().out)["direction"] == direction
    assert cli._lineage_impact(Namespace(database="db", node_id=["one", "two"], max_depth=4)) == 0
    assert json.loads(capsys.readouterr().out)["max_depth"] == 4

    plan_path = tmp_path / "plan.json"

    def fake_plan(
        _research_object: object,
        output: object,
        *,
        overrides: object,
    ) -> Path:
        assert overrides == {"restricted.csv": "exclude"}
        Path(output).write_text('{"status":"ready"}', encoding="utf-8")
        return Path(output)

    overrides = tmp_path / "overrides.json"
    overrides.write_text('{"restricted.csv":"exclude"}', encoding="utf-8")
    monkeypatch.setattr(cli, "build_publication_plan", fake_plan)
    assert (
        cli._publication_plan(
            Namespace(
                research_object="ro",
                output=plan_path,
                overrides=overrides,
            )
        )
        == 0
    )
    assert "status=ready" in capsys.readouterr().out

    monkeypatch.setattr(cli, "validate_publication_plan", lambda *_args: [])
    assert cli._publication_validate(Namespace(plan="plan", research_object="ro")) == 0
    assert "PASS publication" in capsys.readouterr().out
    monkeypatch.setattr(cli, "validate_publication_plan", lambda *_args: ["hash mismatch"])
    assert cli._publication_validate(Namespace(plan="plan", research_object="ro")) == 1
    assert "FAIL hash mismatch" in capsys.readouterr().out
    monkeypatch.setattr(cli, "stage_publication", lambda *_args: tmp_path / "staged")
    assert (
        cli._publication_stage(Namespace(plan="plan", research_object="ro", output_dir=tmp_path))
        == 0
    )
    assert "Publication staging written" in capsys.readouterr().out


@pytest.mark.parametrize(
    "payload",
    [
        "[]",
        '{"path": 3}',
    ],
)
def test_publication_plan_rejects_invalid_overrides(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    payload: str,
) -> None:
    overrides = tmp_path / "overrides.json"
    overrides.write_text(payload, encoding="utf-8")
    with pytest.raises(ValueError, match="JSON object"):
        cli._publication_plan(
            Namespace(research_object="ro", output=tmp_path / "plan.json", overrides=overrides)
        )


def _linz_args(tmp_path: Path, **overrides: object) -> Namespace:
    values = vars(_network_args(tmp_path)).copy()
    values.update(
        {
            "state_store": tmp_path / "state",
            "layer_kind": "layer",
            "layer_id": 50772,
            "primary_key": "id",
            "revision": "100",
            "to_revision": "101",
            "target_database": tmp_path / "target.duckdb",
            "work_dir": tmp_path / "work",
            "receipt": tmp_path / "receipt.json",
            "table_name": "features",
            "base_name": "changeset",
            "crs": "EPSG:2193",
            "applied_at": "2026-07-31T00:00:00Z",
        }
    )
    values.update(overrides)
    return Namespace(**values)


def test_linz_registered_context_and_coordinator(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    import httpx

    import riopa_provenance.capture as capture
    import riopa_provenance.linz as linz
    import riopa_provenance.wfs as wfs

    endpoint = {
        "endpoint_id": "endpoint",
        "enabled": True,
        "capture_strategy": "linz-baseline-plus-changesets",
        "url_template": "https://data.linz.test/services;key={api_key}/wfs",
        "authentication": {
            "type": "api-key",
            "environment_variable": "LINZ_API_KEY",
            "secret_location": "path",
            "credential_name": "api_key",
        },
    }
    monkeypatch.setenv("LINZ_API_KEY", "secret")
    monkeypatch.setattr(cli, "validate_registry", lambda *_args: SimpleNamespace(valid=True))
    monkeypatch.setattr(
        cli,
        "load_registry",
        lambda _path: {"sources": [{"source_id": "source", "endpoints": [endpoint]}]},
    )
    source, selected, key = cli._linz_registered_context(_linz_args(tmp_path))
    assert (source["source_id"], selected, key) == ("source", endpoint, "secret")

    monkeypatch.setattr(httpx, "Client", _FakeHttpClient)
    monkeypatch.setattr(capture, "CaptureStore", lambda path: path)
    monkeypatch.setattr(capture, "CapturePolicy", lambda **kwargs: kwargs)
    monkeypatch.setattr(capture, "HttpCaptureClient", lambda **kwargs: kwargs)
    monkeypatch.setattr(
        wfs,
        "WFSFeatureTypeArchiver",
        lambda client, max_pages: (client, max_pages),
    )
    monkeypatch.setattr(
        linz,
        "LinzChangesetCoordinator",
        lambda archiver: ("coordinator", archiver),
    )
    coordinator, client = cli._linz_coordinator(_linz_args(tmp_path), endpoint)
    assert coordinator[0] == "coordinator"
    assert isinstance(client, _FakeHttpClient)


@pytest.mark.parametrize(
    ("endpoint", "message"),
    [
        (
            {"enabled": False, "capture_strategy": "linz-baseline-plus-changesets"},
            "disabled",
        ),
        ({"enabled": True, "capture_strategy": "download-whole"}, "not configured"),
        (
            {
                "enabled": True,
                "capture_strategy": "linz-baseline-plus-changesets",
                "url": "https://example.test/wfs",
            },
            "one registered path API key",
        ),
    ],
)
def test_linz_registered_context_rejects_invalid_endpoint(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    endpoint: dict[str, object],
    message: str,
) -> None:
    endpoint = {"endpoint_id": "endpoint", **endpoint}
    monkeypatch.setattr(cli, "validate_registry", lambda *_args: SimpleNamespace(valid=True))
    monkeypatch.setattr(
        cli,
        "load_registry",
        lambda _path: {"sources": [{"source_id": "source", "endpoints": [endpoint]}]},
    )
    with pytest.raises(ValueError, match=message):
        cli._linz_registered_context(_linz_args(tmp_path))


def test_linz_capture_and_checkpoint_handlers(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    import riopa_provenance.linz as linz
    import riopa_provenance.spatial as spatial

    endpoint = {"endpoint_id": "endpoint", "expected_crs": "EPSG:2193"}
    monkeypatch.setattr(
        cli,
        "_linz_registered_context",
        lambda _args: ({"source_id": "source"}, endpoint, "secret"),
    )
    client = _FakeHttpClient()
    archive = SimpleNamespace(
        capture_set_id="capture-set",
        manifest_path=tmp_path / "capture-set.json",
        feature_count=2,
    )
    baseline_transition = SimpleNamespace(
        archive=archive,
        state_write=SimpleNamespace(
            state_path=tmp_path / "state.json",
            state={"state_sha256": "a" * 64, "current_revision": "100"},
        ),
    )
    changeset_transition = SimpleNamespace(
        archive=archive,
        state_write=SimpleNamespace(
            state_path=tmp_path / "state.json",
            state={
                "state_sha256": "b" * 64,
                "current_revision": "100",
                "pending_changesets": [{"to_revision": "101"}],
            },
        ),
    )

    class FakeCoordinator:
        def capture_baseline(self, **kwargs: object) -> object:
            assert kwargs["api_key"] == "secret"
            return baseline_transition

        def capture_changeset(self, **kwargs: object) -> object:
            assert kwargs["to_revision"] == "101"
            return changeset_transition

    monkeypatch.setattr(cli, "_linz_coordinator", lambda *_args: (FakeCoordinator(), client))
    assert cli._linz_baseline(_linz_args(tmp_path)) == 0
    assert json.loads(capsys.readouterr().out)["current_revision"] == "100"
    assert client.closed
    client.closed = False
    assert cli._linz_capture_changeset(_linz_args(tmp_path)) == 0
    assert json.loads(capsys.readouterr().out)["pending_to_revision"] == "101"
    assert client.closed

    state = {
        "service_url": "https://example.test/wfs",
        "type_name": "layer-50772",
        "source_id": "source",
        "layer_id": 50772,
        "primary_key": "id",
        "pending_changesets": [
            {
                "manifest_path": "capture-set.json",
                "from_revision": "100",
                "to_revision": "101",
                "capture_set_id": "capture-set",
                "manifest_sha256": "c" * 64,
            }
        ],
    }
    advanced = SimpleNamespace(
        state_path=tmp_path / "advanced.json",
        state={"state_sha256": "d" * 64, "current_revision": "101"},
    )

    class FakeStateStore:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            pass

        def load_current(self) -> dict[str, object]:
            return state

    class FakeCoordinatorClass:
        @staticmethod
        def advance_checkpoint(**kwargs: object) -> object:
            assert kwargs["target_database"] == tmp_path / "target.duckdb"
            return advanced

    monkeypatch.setattr(linz, "LinzStateStore", FakeStateStore)
    monkeypatch.setattr(linz, "LinzChangesetCoordinator", FakeCoordinatorClass)
    monkeypatch.setattr(
        spatial,
        "materialize_wfs_capture_set",
        lambda *args, **kwargs: SimpleNamespace(geoparquet_path=tmp_path / "changes.parquet"),
    )
    application = SimpleNamespace(
        receipt_path=tmp_path / "receipt.json",
        receipt={
            "receipt_sha256": "e" * 64,
            "counts": {"inserted": 2},
            "row_count_after": 2,
        },
    )
    monkeypatch.setattr(linz, "apply_linz_changeset", lambda **kwargs: application)
    assert cli._linz_apply_pending(_linz_args(tmp_path)) == 0
    assert json.loads(capsys.readouterr().out)["current_revision"] == "101"
    assert cli._linz_advance(_linz_args(tmp_path)) == 0
    assert json.loads(capsys.readouterr().out)["state_sha256"] == "d" * 64

    state["pending_changesets"] = []
    with pytest.raises(ValueError, match="exactly one pending"):
        cli._linz_apply_pending(_linz_args(tmp_path))
