"""Command-line interface for the RIOPA reference implementation."""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from .crate import build_research_object, verify_research_object
from .lineage import LineageIndex
from .methods import generate_methods_markdown
from .publication import (
    build_publication_plan,
    stage_publication,
    validate_publication_plan,
)
from .registry import (
    import_district_plans_csv,
    load_registry,
    validate_registry,
    write_registry_json,
)
from .roadmap import (
    render_status_markdown,
    roadmap_status,
    validate_roadmap,
    write_issue_configuration,
)
from .validation import validate_bundle


def _print_json(value: Any) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False))


def _validate(args: argparse.Namespace) -> int:
    results = validate_bundle(args.root)
    failures = 0
    for result in results:
        relative = result.path
        if result.valid:
            print(f"PASS {relative}")
        else:
            failures += 1
            print(f"FAIL {relative}")
            for error in result.errors:
                print(f"  - {error}")
    print(f"Validated {len(results)} item(s); {failures} failure(s).")
    return 1 if failures else 0


def _methods(args: argparse.Namespace) -> int:
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(generate_methods_markdown(args.manifest), encoding="utf-8")
    print(f"Methods written to {output}")
    return 0


def _research_object(args: argparse.Namespace) -> int:
    output = build_research_object(args.manifest, args.output_dir)
    print(f"Research object written to {output}")
    return 0


def _research_object_verify(args: argparse.Namespace) -> int:
    result = verify_research_object(args.root)
    if result.valid:
        print(f"PASS research object {result.root}")
        return 0
    print(f"FAIL research object {result.root}")
    for error in result.errors:
        print(f"  - {error}")
    return 1


def _registry_validate(args: argparse.Namespace) -> int:
    result = validate_registry(args.registry, args.schema)
    if result.valid:
        print(f"PASS source registry {result.path}")
        return 0
    print(f"FAIL source registry {result.path}")
    for error in result.errors:
        print(f"  - {error}")
    return 1


def _registry_import(args: argparse.Namespace) -> int:
    registry = import_district_plans_csv(
        args.csv,
        generated_at=args.generated_at,
        catalogue_url=args.catalogue_url,
    )
    output = write_registry_json(registry, args.output)
    print(f"Source registry written to {output}")
    return 0


def _find_registry_endpoint(
    registry: dict[str, Any], source_id: str, endpoint_id: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    source = next(
        (item for item in registry.get("sources", []) if item.get("source_id") == source_id),
        None,
    )
    if source is None:
        raise ValueError(f"source is not registered: {source_id}")
    endpoint = next(
        (item for item in source.get("endpoints", []) if item.get("endpoint_id") == endpoint_id),
        None,
    )
    if endpoint is None:
        raise ValueError(f"endpoint is not registered for {source_id}: {endpoint_id}")
    return source, endpoint


def _registered_auth(
    endpoint: Mapping[str, Any],
) -> tuple[str, dict[str, str], dict[str, str], list[str]]:
    """Resolve a registered credential without ever returning it for logging."""

    authentication = endpoint.get("authentication") or {"type": "none"}
    auth_type = authentication.get("type", "none")
    url = str(endpoint.get("url_template") or endpoint["url"])
    if auth_type == "none":
        return url, {}, {}, []
    if auth_type != "api-key":
        raise ValueError(f"automatic capture does not support authentication type {auth_type!r}")
    environment_variable = authentication.get("environment_variable")
    if not isinstance(environment_variable, str) or not environment_variable:
        raise ValueError("registered API-key endpoint has no environment variable")
    secret = os.environ.get(environment_variable)
    if not secret:
        raise ValueError(
            f"required credential environment variable is unset: {environment_variable}"
        )
    location = authentication.get("secret_location")
    credential_name = authentication.get("credential_name")
    params: dict[str, str] = {}
    headers: dict[str, str] = {}
    if location == "query":
        params[str(credential_name or "key")] = secret
    elif location == "header":
        headers[str(credential_name or "X-API-Key")] = secret
    elif location == "path":
        placeholder = "{" + str(credential_name or "api_key") + "}"
        if placeholder not in url:
            raise ValueError(f"registered path credential template does not contain {placeholder}")
        url = url.replace(placeholder, secret)
    else:
        raise ValueError(f"unsupported API-key secret location: {location!r}")
    return url, params, headers, [secret]


def _archive_arcgis(args: argparse.Namespace) -> int:
    # Imported lazily so metadata-only and roadmap users do not need spatial extras.
    import httpx

    from .arcgis import ArcGISFeatureLayerArchiver
    from .capture import CapturePolicy, CaptureStore, HttpCaptureClient

    registry_result = validate_registry(args.registry, args.schema)
    if not registry_result.valid:
        raise ValueError("source registry is invalid: " + "; ".join(registry_result.errors))
    registry = load_registry(args.registry)
    source, endpoint = _find_registry_endpoint(registry, args.source_id, args.endpoint_id)
    if not endpoint.get("enabled"):
        raise ValueError("endpoint is disabled in the source registry")
    if endpoint.get("mechanism") not in {"arcgis-feature-service", "arcgis-map-service"}:
        raise ValueError(f"endpoint is not an ArcGIS service: {endpoint.get('mechanism')}")
    layer_ids = endpoint.get("layer_ids", [])
    layer_id = args.layer_id
    if layer_id is None:
        if len(layer_ids) != 1:
            raise ValueError("--layer-id is required when the registry declares multiple layers")
        layer_id = int(layer_ids[0])
    elif layer_ids and layer_id not in layer_ids:
        raise ValueError(f"layer {layer_id} is not declared for the registered endpoint")
    service_url, auth_params, auth_headers, redact_values = _registered_auth(endpoint)
    host = urlsplit(service_url).hostname
    if not host:
        raise ValueError("registered ArcGIS endpoint has no host")

    timeout = httpx.Timeout(
        connect=args.connect_timeout,
        read=args.read_timeout,
        write=args.connect_timeout,
        pool=args.connect_timeout,
    )
    limits = httpx.Limits(max_connections=4, max_keepalive_connections=2)
    with httpx.Client(
        timeout=timeout,
        limits=limits,
        trust_env=args.trust_environment,
    ) as http_client:
        capture_client = HttpCaptureClient(
            client=http_client,
            store=CaptureStore(Path(args.store)),
            policy=CapturePolicy(
                allowed_hosts=frozenset({host}),
                max_response_bytes=args.max_response_bytes,
            ),
        )
        archive = ArcGISFeatureLayerArchiver(
            capture_client, max_pages=args.max_pages
        ).archive_layer(
            source_id=source["source_id"],
            endpoint_id=endpoint["endpoint_id"],
            service_url=service_url,
            layer_id=layer_id,
            where=args.where,
            out_fields=args.out_fields,
            request_params=auth_params,
            headers=auth_headers,
            redact_values=redact_values,
        )
    _print_json(
        {
            "capture_set_id": archive.capture_set_id,
            "source_id": archive.source_id,
            "service_url": archive.service_url,
            "layer_id": archive.layer_id,
            "feature_count": archive.feature_count,
            "capture_count": 1 + len(archive.page_captures),
            "manifest_path": str(archive.manifest_path),
        }
    )
    return 0


def _archive_wfs(args: argparse.Namespace) -> int:
    import httpx

    from .capture import CapturePolicy, CaptureStore, HttpCaptureClient
    from .wfs import WFSFeatureTypeArchiver

    registry_result = validate_registry(args.registry, args.schema)
    if not registry_result.valid:
        raise ValueError("source registry is invalid: " + "; ".join(registry_result.errors))
    registry = load_registry(args.registry)
    source, endpoint = _find_registry_endpoint(registry, args.source_id, args.endpoint_id)
    if not endpoint.get("enabled"):
        raise ValueError("endpoint is disabled in the source registry")
    if endpoint.get("mechanism") != "wfs":
        raise ValueError(f"endpoint is not WFS: {endpoint.get('mechanism')}")
    service_url, auth_params, auth_headers, redact_values = _registered_auth(endpoint)
    host = urlsplit(service_url).hostname
    if not host:
        raise ValueError("registered WFS endpoint has no host")
    timeout = httpx.Timeout(
        connect=args.connect_timeout,
        read=args.read_timeout,
        write=args.connect_timeout,
        pool=args.connect_timeout,
    )
    with httpx.Client(
        timeout=timeout,
        limits=httpx.Limits(max_connections=4, max_keepalive_connections=2),
        trust_env=args.trust_environment,
    ) as http_client:
        capture_client = HttpCaptureClient(
            client=http_client,
            store=CaptureStore(Path(args.store)),
            policy=CapturePolicy(
                allowed_hosts=frozenset({host}),
                max_response_bytes=args.max_response_bytes,
            ),
        )
        archive = WFSFeatureTypeArchiver(
            capture_client, max_pages=args.max_pages
        ).archive_feature_type(
            source_id=source["source_id"],
            endpoint_id=endpoint["endpoint_id"],
            service_url=service_url,
            type_name=args.type_name,
            page_size=args.page_size,
            sort_by=args.sort_by,
            id_property=args.id_property,
            srs_name=args.srs_name or endpoint.get("expected_crs"),
            cql_filter=args.cql_filter,
            request_params=auth_params,
            headers=auth_headers,
            redact_values=redact_values,
        )
    _print_json(
        {
            "capture_set_id": archive.capture_set_id,
            "source_id": archive.source_id,
            "service_url": archive.service_url,
            "type_name": archive.type_name,
            "feature_count": archive.feature_count,
            "capture_count": 2 + len(archive.page_captures),
            "manifest_path": str(archive.manifest_path),
        }
    )
    return 0


def _archive_resource(args: argparse.Namespace) -> int:
    import httpx

    from .capture import CapturePolicy, CaptureStore, HttpCaptureClient

    registry_result = validate_registry(args.registry, args.schema)
    if not registry_result.valid:
        raise ValueError("source registry is invalid: " + "; ".join(registry_result.errors))
    registry = load_registry(args.registry)
    source, endpoint = _find_registry_endpoint(registry, args.source_id, args.endpoint_id)
    if not endpoint.get("enabled"):
        raise ValueError("endpoint is disabled in the source registry")
    if endpoint.get("capture_strategy") not in {"download-whole", "metadata-only"}:
        raise ValueError("registered endpoint is not configured for whole-resource capture")
    url, auth_params, auth_headers, redact_values = _registered_auth(endpoint)
    host = urlsplit(url).hostname
    if not host:
        raise ValueError("registered endpoint has no host")
    timeout = httpx.Timeout(
        connect=args.connect_timeout,
        read=args.read_timeout,
        write=args.connect_timeout,
        pool=args.connect_timeout,
    )
    with httpx.Client(timeout=timeout, trust_env=args.trust_environment) as http_client:
        result = HttpCaptureClient(
            client=http_client,
            store=CaptureStore(Path(args.store)),
            policy=CapturePolicy(
                allowed_hosts=frozenset({host}),
                max_response_bytes=args.max_response_bytes,
            ),
        ).capture(
            "GET",
            url,
            source_id=source["source_id"],
            endpoint_id=endpoint["endpoint_id"],
            params=auth_params,
            headers=auth_headers,
            redact_values=redact_values,
        )
    _print_json(
        {
            "capture_id": result.capture_id,
            "source_id": result.source_id,
            "endpoint_id": result.endpoint_id,
            "status_code": result.status_code,
            "object_sha256": result.object_sha256,
            "size_bytes": result.size_bytes,
            "object_path": str(result.object_path),
            "metadata_path": str(result.metadata_path),
        }
    )
    return 0


def _linz_registered_context(
    args: argparse.Namespace,
) -> tuple[dict[str, Any], dict[str, Any], str]:
    registry_result = validate_registry(args.registry, args.schema)
    if not registry_result.valid:
        raise ValueError("source registry is invalid: " + "; ".join(registry_result.errors))
    registry = load_registry(args.registry)
    source, endpoint = _find_registry_endpoint(registry, args.source_id, args.endpoint_id)
    if not endpoint.get("enabled"):
        raise ValueError("endpoint is disabled in the source registry")
    if endpoint.get("capture_strategy") != "linz-baseline-plus-changesets":
        raise ValueError("registered endpoint is not configured for LINZ changesets")
    service_url, auth_params, auth_headers, redact_values = _registered_auth(endpoint)
    if auth_params or auth_headers or len(redact_values) != 1:
        raise ValueError("LINZ changeset capture requires one registered path API key")
    if not service_url.endswith("/wfs"):
        raise ValueError("registered LINZ URL template must resolve to the WFS endpoint")
    return source, endpoint, redact_values[0]


def _linz_coordinator(args: argparse.Namespace, endpoint: Mapping[str, Any]) -> tuple[Any, Any]:
    import httpx

    from .capture import CapturePolicy, CaptureStore, HttpCaptureClient
    from .linz import LinzChangesetCoordinator
    from .wfs import WFSFeatureTypeArchiver

    host = urlsplit(str(endpoint.get("url_template") or endpoint["url"])).hostname
    if not host:
        raise ValueError("registered LINZ endpoint has no host")
    timeout = httpx.Timeout(
        connect=args.connect_timeout,
        read=args.read_timeout,
        write=args.connect_timeout,
        pool=args.connect_timeout,
    )
    http_client = httpx.Client(
        timeout=timeout,
        limits=httpx.Limits(max_connections=4, max_keepalive_connections=2),
        trust_env=args.trust_environment,
    )
    capture_client = HttpCaptureClient(
        client=http_client,
        store=CaptureStore(Path(args.capture_store)),
        policy=CapturePolicy(
            allowed_hosts=frozenset({host}),
            max_response_bytes=args.max_response_bytes,
        ),
    )
    return LinzChangesetCoordinator(
        WFSFeatureTypeArchiver(capture_client, max_pages=args.max_pages)
    ), http_client


def _linz_baseline(args: argparse.Namespace) -> int:
    from .linz import LinzStateStore

    source, endpoint, api_key = _linz_registered_context(args)
    coordinator, http_client = _linz_coordinator(args, endpoint)
    try:
        transition = coordinator.capture_baseline(
            state_store=LinzStateStore(
                args.state_store, layer_kind=args.layer_kind, layer_id=args.layer_id
            ),
            api_key=api_key,
            source_id=source["source_id"],
            endpoint_id=endpoint["endpoint_id"],
            primary_key=args.primary_key,
            revision=args.revision,
            page_size=args.page_size,
            srs_name=args.srs_name or endpoint.get("expected_crs") or "EPSG:2193",
        )
    finally:
        http_client.close()
    _print_json(
        {
            "capture_set_id": transition.archive.capture_set_id,
            "manifest_path": str(transition.archive.manifest_path),
            "feature_count": transition.archive.feature_count,
            "state_path": str(transition.state_write.state_path),
            "state_sha256": transition.state_write.state["state_sha256"],
            "current_revision": transition.state_write.state["current_revision"],
        }
    )
    return 0


def _linz_capture_changeset(args: argparse.Namespace) -> int:
    from .linz import LinzStateStore

    _, endpoint, api_key = _linz_registered_context(args)
    coordinator, http_client = _linz_coordinator(args, endpoint)
    try:
        transition = coordinator.capture_changeset(
            state_store=LinzStateStore(
                args.state_store, layer_kind=args.layer_kind, layer_id=args.layer_id
            ),
            api_key=api_key,
            to_revision=args.to_revision,
            page_size=args.page_size,
            srs_name=args.srs_name or endpoint.get("expected_crs") or "EPSG:2193",
            cql_filter=args.cql_filter,
        )
    finally:
        http_client.close()
    _print_json(
        {
            "capture_set_id": transition.archive.capture_set_id,
            "manifest_path": str(transition.archive.manifest_path),
            "feature_count": transition.archive.feature_count,
            "state_path": str(transition.state_write.state_path),
            "state_sha256": transition.state_write.state["state_sha256"],
            "checkpoint_revision": transition.state_write.state["current_revision"],
            "pending_to_revision": transition.state_write.state["pending_changesets"][0][
                "to_revision"
            ],
        }
    )
    return 0


def _linz_apply_pending(args: argparse.Namespace) -> int:
    from .linz import LinzChangesetCoordinator, LinzStateStore, apply_linz_changeset
    from .spatial import materialize_wfs_capture_set

    state_store = LinzStateStore(
        args.state_store, layer_kind=args.layer_kind, layer_id=args.layer_id
    )
    state = state_store.load_current()
    assert state is not None
    if len(state["pending_changesets"]) != 1:
        raise ValueError("exactly one pending LINZ changeset is required")
    pending = state["pending_changesets"][0]
    capture_root = Path(args.capture_store).resolve()
    capture_set_path = capture_root / pending["manifest_path"]
    canonical_layer_id = f"{state['service_url']}#{state['type_name']}"
    materialization = materialize_wfs_capture_set(
        capture_set_path,
        store_root=capture_root,
        output_dir=args.work_dir,
        crs=args.crs,
        base_name=args.base_name,
        canonical_layer_id=canonical_layer_id,
    )
    application = apply_linz_changeset(
        target_database=args.target_database,
        changeset_parquet=materialization.geoparquet_path,
        source_id=state["source_id"],
        layer_id=state["layer_id"],
        primary_key=state["primary_key"],
        from_revision=pending["from_revision"],
        to_revision=pending["to_revision"],
        capture_set_id=pending["capture_set_id"],
        capture_set_manifest_sha256=pending["manifest_sha256"],
        receipt_path=args.receipt,
        table_name=args.table_name,
        applied_at=args.applied_at,
    )
    advanced = LinzChangesetCoordinator.advance_checkpoint(
        state_store=state_store,
        receipt_path=application.receipt_path,
        target_database=args.target_database,
    )
    _print_json(
        {
            "receipt_path": str(application.receipt_path),
            "receipt_sha256": application.receipt["receipt_sha256"],
            "counts": application.receipt["counts"],
            "row_count_after": application.receipt["row_count_after"],
            "state_path": str(advanced.state_path),
            "current_revision": advanced.state["current_revision"],
        }
    )
    return 0


def _linz_advance(args: argparse.Namespace) -> int:
    from .linz import LinzChangesetCoordinator, LinzStateStore

    state_store = LinzStateStore(
        args.state_store, layer_kind=args.layer_kind, layer_id=args.layer_id
    )
    advanced = LinzChangesetCoordinator.advance_checkpoint(
        state_store=state_store,
        receipt_path=args.receipt,
        target_database=args.target_database,
    )
    _print_json(
        {
            "state_path": str(advanced.state_path),
            "state_sha256": advanced.state["state_sha256"],
            "current_revision": advanced.state["current_revision"],
        }
    )
    return 0


def _spatial_geojson(args: argparse.Namespace) -> int:
    from .spatial import materialize_geojson

    result = materialize_geojson(
        args.input,
        output_dir=args.output_dir,
        source_id=args.source_id,
        layer_id=args.layer_id,
        capture_id=args.capture_id,
        crs=args.crs,
        object_id_field=args.object_id_field,
        base_name=args.base_name,
    )
    _print_json(
        {
            "geoparquet": str(result.geoparquet_path),
            "duckdb": str(result.duckdb_path),
            "quality_report": str(result.quality_report_path),
            "feature_count": result.feature_count,
            "geoparquet_sha256": result.geoparquet_sha256,
            "duckdb_sha256": result.duckdb_sha256,
        }
    )
    return 0


def _spatial_arcgis(args: argparse.Namespace) -> int:
    from .spatial import materialize_arcgis_capture_set

    result = materialize_arcgis_capture_set(
        args.capture_set,
        store_root=args.store,
        output_dir=args.output_dir,
        crs=args.crs,
        base_name=args.base_name,
    )
    _print_json(
        {
            "geoparquet": str(result.geoparquet_path),
            "duckdb": str(result.duckdb_path),
            "quality_report": str(result.quality_report_path),
            "feature_count": result.feature_count,
            "geoparquet_sha256": result.geoparquet_sha256,
            "duckdb_sha256": result.duckdb_sha256,
        }
    )
    return 0


def _spatial_wfs(args: argparse.Namespace) -> int:
    from .spatial import materialize_wfs_capture_set

    result = materialize_wfs_capture_set(
        args.capture_set,
        store_root=args.store,
        output_dir=args.output_dir,
        crs=args.crs,
        base_name=args.base_name,
        canonical_layer_id=args.canonical_layer_id,
    )
    _print_json(
        {
            "geoparquet": str(result.geoparquet_path),
            "duckdb": str(result.duckdb_path),
            "quality_report": str(result.quality_report_path),
            "feature_count": result.feature_count,
            "geoparquet_sha256": result.geoparquet_sha256,
            "duckdb_sha256": result.duckdb_sha256,
        }
    )
    return 0


def _lineage_build(args: argparse.Namespace) -> int:
    index = LineageIndex(args.database)
    snapshot_id = index.import_manifest(args.manifest, schema_dir=args.schema_dir)
    print(f"Lineage index written to {index.path} for {snapshot_id}")
    return 0


def _lineage_walk(args: argparse.Namespace) -> int:
    index = LineageIndex(args.database)
    result = (
        index.upstream(args.node_id, max_depth=args.max_depth)
        if args.direction == "upstream"
        else index.downstream(args.node_id, max_depth=args.max_depth)
    )
    _print_json({"node_id": args.node_id, "direction": args.direction, "nodes": result})
    return 0


def _lineage_impact(args: argparse.Namespace) -> int:
    _print_json(LineageIndex(args.database).rebuild_impact(args.node_id, max_depth=args.max_depth))
    return 0


def _lineage_query(args: argparse.Namespace) -> int:
    """Answer one bounded local query with a cache/projection diagnostic envelope."""

    result = LineageIndex(args.database).query_cached(
        args.node_id, question=args.question, max_depth=args.max_depth
    )
    if args.page_size is not None:
        answer = result["answer"]
        if not isinstance(answer, list):
            raise ValueError("--page-size is only valid for list-valued answers")
        if args.page_size < 1 or args.page_size > 1000:
            raise ValueError("--page-size must be between 1 and 1000")
        offset = args.offset
        if offset < 0:
            raise ValueError("--offset must be non-negative")
        result["answer"] = answer[offset : offset + args.page_size]
        result["pagination"] = {
            "limit": args.page_size,
            "offset": offset,
            "total": len(answer),
            "next_offset": (
                offset + args.page_size if offset + args.page_size < len(answer) else None
            ),
        }
    _print_json(result)
    return 0


def _lineage_export_prov_jsonld(args: argparse.Namespace) -> int:
    output = LineageIndex(args.database).export_prov_jsonld(args.output)
    print(f"PROV JSON-LD projection written to {output}")
    return 0


def _lineage_nodes(args: argparse.Namespace) -> int:
    _print_json(
        LineageIndex(args.database).page_nodes(
            node_type=args.node_type, limit=args.limit, offset=args.offset
        )
    )
    return 0


def _publication_plan(args: argparse.Namespace) -> int:
    overrides: dict[str, str] | None = None
    if args.overrides:
        value = json.loads(Path(args.overrides).read_text(encoding="utf-8"))
        if not isinstance(value, dict) or not all(
            isinstance(key, str) and isinstance(item, str) for key, item in value.items()
        ):
            raise ValueError("publication overrides must be a JSON object of path-to-decision")
        overrides = value
    output = build_publication_plan(
        args.research_object,
        args.output,
        overrides=overrides,
    )
    plan = json.loads(output.read_text(encoding="utf-8"))
    print(f"Publication plan written to {output}; status={plan['status']}")
    return 0 if plan["status"] == "ready" else 2


def _publication_validate(args: argparse.Namespace) -> int:
    errors = validate_publication_plan(args.plan, args.research_object)
    if not errors:
        print("PASS publication plan and research-object binding")
        return 0
    for error in errors:
        print(f"FAIL {error}")
    return 1


def _publication_stage(args: argparse.Namespace) -> int:
    output = stage_publication(args.plan, args.research_object, args.output_dir)
    print(f"Publication staging written to {output}")
    return 0


def _roadmap_validate(args: argparse.Namespace) -> int:
    problems = validate_roadmap(args.root, check_generated_issues=not args.skip_issue_drift)
    if problems:
        for problem in problems:
            print(f"FAIL {problem}")
        print(f"Roadmap validation failed with {len(problems)} problem(s).")
        return 1
    print("PASS roadmap, maturity, release, track, evidence, and issue-graph validation")
    return 0


def _roadmap_status(args: argparse.Namespace) -> int:
    status = roadmap_status(args.root, args.release)
    text = (
        json.dumps(status, indent=2, ensure_ascii=False) + "\n"
        if args.format == "json"
        else render_status_markdown(status)
    )
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
        print(f"Roadmap status written to {output}")
    else:
        print(text, end="")
    return 0


def _roadmap_generate_issues(args: argparse.Namespace) -> int:
    output = write_issue_configuration(args.root, args.output)
    print(f"Issue configuration written to {output}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="riopa")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate schemas and research bundles")
    validate.add_argument("--root", default=".")
    validate.set_defaults(func=_validate)

    methods = subparsers.add_parser("methods", help="generate methods from a manifest")
    methods.add_argument("--manifest", required=True)
    methods.add_argument("--output", required=True)
    methods.set_defaults(func=_methods)

    crate = subparsers.add_parser("research-object", help="build a closed research object")
    crate.add_argument("--manifest", required=True)
    crate.add_argument("--output-dir", required=True)
    crate.set_defaults(func=_research_object)

    crate_verify = subparsers.add_parser(
        "research-object-verify", help="verify research-object closure and checksums"
    )
    crate_verify.add_argument("--root", required=True)
    crate_verify.set_defaults(func=_research_object_verify)

    registry = subparsers.add_parser("registry", help="manage spatial source registries")
    registry_subparsers = registry.add_subparsers(dest="registry_command", required=True)
    registry_validate = registry_subparsers.add_parser("validate")
    registry_validate.add_argument("--registry", required=True)
    registry_validate.add_argument("--schema", default="schemas/source-registry.schema.json")
    registry_validate.set_defaults(func=_registry_validate)
    registry_import = registry_subparsers.add_parser("import-district-plans")
    registry_import.add_argument("--csv", required=True)
    registry_import.add_argument("--output", required=True)
    registry_import.add_argument("--generated-at", required=True)
    registry_import.add_argument("--catalogue-url", default="https://district-plans.nz/")
    registry_import.set_defaults(func=_registry_import)

    archive = subparsers.add_parser("archive", help="capture registered source bytes")
    archive_subparsers = archive.add_subparsers(dest="archive_command", required=True)
    arcgis = archive_subparsers.add_parser("arcgis-layer")
    arcgis.add_argument("--registry", required=True)
    arcgis.add_argument("--schema", default="schemas/source-registry.schema.json")
    arcgis.add_argument("--source-id", required=True)
    arcgis.add_argument("--endpoint-id", required=True)
    arcgis.add_argument("--layer-id", type=int)
    arcgis.add_argument("--store", required=True)
    arcgis.add_argument("--where", default="1=1")
    arcgis.add_argument("--out-fields", default="*")
    arcgis.add_argument("--max-pages", type=int, default=100_000)
    arcgis.add_argument("--max-response-bytes", type=int, default=512 * 1024 * 1024)
    arcgis.add_argument("--connect-timeout", type=float, default=30.0)
    arcgis.add_argument("--read-timeout", type=float, default=300.0)
    arcgis.add_argument("--trust-environment", action="store_true")
    arcgis.set_defaults(func=_archive_arcgis)
    wfs = archive_subparsers.add_parser("wfs-feature-type")
    wfs.add_argument("--registry", required=True)
    wfs.add_argument("--schema", default="schemas/source-registry.schema.json")
    wfs.add_argument("--source-id", required=True)
    wfs.add_argument("--endpoint-id", required=True)
    wfs.add_argument("--type-name", required=True)
    wfs.add_argument("--store", required=True)
    wfs.add_argument("--page-size", type=int, default=1000)
    wfs.add_argument("--sort-by")
    wfs.add_argument("--id-property")
    wfs.add_argument("--srs-name")
    wfs.add_argument("--cql-filter")
    wfs.add_argument("--max-pages", type=int, default=100_000)
    wfs.add_argument("--max-response-bytes", type=int, default=512 * 1024 * 1024)
    wfs.add_argument("--connect-timeout", type=float, default=30.0)
    wfs.add_argument("--read-timeout", type=float, default=300.0)
    wfs.add_argument("--trust-environment", action="store_true")
    wfs.set_defaults(func=_archive_wfs)
    resource = archive_subparsers.add_parser("resource")
    resource.add_argument("--registry", required=True)
    resource.add_argument("--schema", default="schemas/source-registry.schema.json")
    resource.add_argument("--source-id", required=True)
    resource.add_argument("--endpoint-id", required=True)
    resource.add_argument("--store", required=True)
    resource.add_argument("--max-response-bytes", type=int, default=1024 * 1024 * 1024)
    resource.add_argument("--connect-timeout", type=float, default=30.0)
    resource.add_argument("--read-timeout", type=float, default=600.0)
    resource.add_argument("--trust-environment", action="store_true")
    resource.set_defaults(func=_archive_resource)

    linz = subparsers.add_parser(
        "linz", help="manage LINZ baselines, changesets, and revision checkpoints"
    )
    linz_subparsers = linz.add_subparsers(dest="linz_command", required=True)

    def add_linz_identity(parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--state-store", required=True)
        parser.add_argument("--layer-kind", choices=("layer", "table"), required=True)
        parser.add_argument("--layer-id", type=int, required=True)

    def add_linz_network(parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--registry", required=True)
        parser.add_argument("--schema", default="schemas/source-registry.schema.json")
        parser.add_argument("--source-id", required=True)
        parser.add_argument("--endpoint-id", required=True)
        parser.add_argument("--capture-store", required=True)
        parser.add_argument("--page-size", type=int, default=1000)
        parser.add_argument("--srs-name")
        parser.add_argument("--max-pages", type=int, default=100_000)
        parser.add_argument("--max-response-bytes", type=int, default=512 * 1024 * 1024)
        parser.add_argument("--connect-timeout", type=float, default=30.0)
        parser.add_argument("--read-timeout", type=float, default=300.0)
        parser.add_argument("--trust-environment", action="store_true")

    linz_baseline = linz_subparsers.add_parser("baseline")
    add_linz_identity(linz_baseline)
    add_linz_network(linz_baseline)
    linz_baseline.add_argument("--primary-key", required=True)
    linz_baseline.add_argument("--revision", required=True)
    linz_baseline.set_defaults(func=_linz_baseline)

    linz_changeset = linz_subparsers.add_parser("capture-changeset")
    add_linz_identity(linz_changeset)
    add_linz_network(linz_changeset)
    linz_changeset.add_argument("--to-revision", required=True)
    linz_changeset.add_argument("--cql-filter")
    linz_changeset.set_defaults(func=_linz_capture_changeset)

    linz_apply = linz_subparsers.add_parser("apply-pending")
    add_linz_identity(linz_apply)
    linz_apply.add_argument("--capture-store", required=True)
    linz_apply.add_argument("--target-database", required=True)
    linz_apply.add_argument("--work-dir", required=True)
    linz_apply.add_argument("--receipt", required=True)
    linz_apply.add_argument("--table-name", default="features")
    linz_apply.add_argument("--base-name", default="linz-changeset")
    linz_apply.add_argument("--crs")
    linz_apply.add_argument("--applied-at")
    linz_apply.set_defaults(func=_linz_apply_pending)

    linz_advance = linz_subparsers.add_parser("advance-checkpoint")
    add_linz_identity(linz_advance)
    linz_advance.add_argument("--receipt", required=True)
    linz_advance.add_argument("--target-database", required=True)
    linz_advance.set_defaults(func=_linz_advance)

    spatial = subparsers.add_parser("spatial", help="build canonical spatial materialisations")
    spatial_subparsers = spatial.add_subparsers(dest="spatial_command", required=True)
    geojson = spatial_subparsers.add_parser("geojson")
    geojson.add_argument("--input", required=True)
    geojson.add_argument("--output-dir", required=True)
    geojson.add_argument("--source-id", required=True)
    geojson.add_argument("--layer-id", required=True)
    geojson.add_argument("--capture-id", required=True)
    geojson.add_argument("--crs")
    geojson.add_argument("--object-id-field")
    geojson.add_argument("--base-name", default="features")
    geojson.set_defaults(func=_spatial_geojson)
    arcgis_spatial = spatial_subparsers.add_parser("arcgis-capture-set")
    arcgis_spatial.add_argument("--capture-set", required=True)
    arcgis_spatial.add_argument("--store", required=True)
    arcgis_spatial.add_argument("--output-dir", required=True)
    arcgis_spatial.add_argument("--crs")
    arcgis_spatial.add_argument("--base-name", default="features")
    arcgis_spatial.set_defaults(func=_spatial_arcgis)
    wfs_spatial = spatial_subparsers.add_parser("wfs-capture-set")
    wfs_spatial.add_argument("--capture-set", required=True)
    wfs_spatial.add_argument("--store", required=True)
    wfs_spatial.add_argument("--output-dir", required=True)
    wfs_spatial.add_argument("--crs")
    wfs_spatial.add_argument("--base-name", default="features")
    wfs_spatial.add_argument("--canonical-layer-id")
    wfs_spatial.set_defaults(func=_spatial_wfs)

    lineage = subparsers.add_parser("lineage", help="build and query provenance lineage")
    lineage_subparsers = lineage.add_subparsers(dest="lineage_command", required=True)
    lineage_build = lineage_subparsers.add_parser("build")
    lineage_build.add_argument("--manifest", required=True)
    lineage_build.add_argument("--database", required=True)
    lineage_build.add_argument("--schema-dir")
    lineage_build.set_defaults(func=_lineage_build)
    lineage_walk = lineage_subparsers.add_parser("walk")
    lineage_walk.add_argument("--database", required=True)
    lineage_walk.add_argument("--node-id", required=True)
    lineage_walk.add_argument("--direction", choices=("upstream", "downstream"), required=True)
    lineage_walk.add_argument("--max-depth", type=int, default=20)
    lineage_walk.set_defaults(func=_lineage_walk)
    lineage_impact = lineage_subparsers.add_parser("impact")
    lineage_impact.add_argument("--database", required=True)
    lineage_impact.add_argument("--node-id", action="append", required=True)
    lineage_impact.add_argument("--max-depth", type=int, default=50)
    lineage_impact.set_defaults(func=_lineage_impact)
    lineage_query = lineage_subparsers.add_parser(
        "query", help="answer a bounded local where/why/how query"
    )
    lineage_query.add_argument("--database", required=True)
    lineage_query.add_argument("--node-id", required=True)
    lineage_query.add_argument("--question", choices=("where", "why", "how"), required=True)
    lineage_query.add_argument("--max-depth", type=int, default=20)
    lineage_query.add_argument("--page-size", type=int)
    lineage_query.add_argument("--offset", type=int, default=0)
    lineage_query.set_defaults(func=_lineage_query)
    lineage_export = lineage_subparsers.add_parser(
        "export-prov-jsonld",
        help="write a deterministic, non-authoritative PROV JSON-LD projection",
    )
    lineage_export.add_argument("--database", required=True)
    lineage_export.add_argument("--output", required=True)
    lineage_export.set_defaults(func=_lineage_export_prov_jsonld)
    lineage_nodes = lineage_subparsers.add_parser(
        "nodes", help="list a bounded page of lineage nodes with diagnostics"
    )
    lineage_nodes.add_argument("--database", required=True)
    lineage_nodes.add_argument("--node-type")
    lineage_nodes.add_argument("--limit", type=int, default=100)
    lineage_nodes.add_argument("--offset", type=int, default=0)
    lineage_nodes.set_defaults(func=_lineage_nodes)

    publication = subparsers.add_parser(
        "publication", help="plan and stage rights-aware federated releases"
    )
    publication_subparsers = publication.add_subparsers(dest="publication_command", required=True)
    publication_plan = publication_subparsers.add_parser("plan")
    publication_plan.add_argument("--research-object", required=True)
    publication_plan.add_argument("--output", required=True)
    publication_plan.add_argument("--overrides")
    publication_plan.set_defaults(func=_publication_plan)
    publication_validate = publication_subparsers.add_parser("validate")
    publication_validate.add_argument("--plan", required=True)
    publication_validate.add_argument("--research-object", required=True)
    publication_validate.set_defaults(func=_publication_validate)
    publication_stage = publication_subparsers.add_parser("stage")
    publication_stage.add_argument("--plan", required=True)
    publication_stage.add_argument("--research-object", required=True)
    publication_stage.add_argument("--output-dir", required=True)
    publication_stage.set_defaults(func=_publication_stage)

    roadmap = subparsers.add_parser("roadmap", help="validate and report the v1 roadmap")
    roadmap_subparsers = roadmap.add_subparsers(dest="roadmap_command", required=True)
    roadmap_validate = roadmap_subparsers.add_parser(
        "validate", help="validate tracks, releases, maturity gates, and generated issues"
    )
    roadmap_validate.add_argument("--root", default=".")
    roadmap_validate.add_argument("--skip-issue-drift", action="store_true")
    roadmap_validate.set_defaults(func=_roadmap_validate)
    roadmap_status_parser = roadmap_subparsers.add_parser(
        "status", help="report readiness for one or every planned release"
    )
    roadmap_status_parser.add_argument("--root", default=".")
    roadmap_status_parser.add_argument("--release")
    roadmap_status_parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    roadmap_status_parser.add_argument("--output")
    roadmap_status_parser.set_defaults(func=_roadmap_status)
    roadmap_issues = roadmap_subparsers.add_parser(
        "generate-issues", help="regenerate project/issues.yaml from Conductor tracks"
    )
    roadmap_issues.add_argument("--root", default=".")
    roadmap_issues.add_argument("--output")
    roadmap_issues.set_defaults(func=_roadmap_generate_issues)
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        code = args.func(args)
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        code = 1
    raise SystemExit(code)


if __name__ == "__main__":
    main(sys.argv[1:])
