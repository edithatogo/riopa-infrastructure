"""Bounded integration contracts for the supermarket-health reference pilot."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from math import isfinite
from typing import Any

from .analysis import build_service_pareto_report
from .hashing import sha256_json


class SupermarketPilotError(ValueError):
    """Raised when supplied pilot evidence cannot support a safe reference packet."""


_ACCESS_MEASURES = ("distance", "network", "multimodal", "capacity", "competition")
_CONTEXT_FIELDS = ("deprivation", "demographic", "rurality")
_ALTERNATIVE_METRICS = (
    "average_access",
    "worst_case_access",
    "subgroup_gap",
    "capacity_served",
    "competition_balance",
    "cost",
    "robustness_loss",
)
_REQUIRED_NON_MODELLED = {"market", "land", "community", "consent"}
_SENSITIVITY_TYPES = {
    "bounded_spatial_confounding_sensitivity",
    "bounded_maup_sensitivity",
    "bounded_measurement_error_sensitivity",
}


def build_archived_supermarket_snapshot(
    payload: Mapping[str, Any],
    *,
    source_id: str,
    registry_version: str,
    licence: str,
    observed_at: str,
    payload_sha256: str,
) -> dict[str, Any]:
    """Convert an archived GeoJSON food-premise payload into bounded assertions.

    The payload must already have been retrieved from a content-addressed
    archive. This function never contacts a source and treats the publisher's
    premise type as a classification, not proof of operation or authority.
    """

    for name, value in (
        ("source_id", source_id),
        ("registry_version", registry_version),
        ("licence", licence),
        ("observed_at", observed_at),
        ("payload_sha256", payload_sha256),
    ):
        if not isinstance(value, str) or not value.strip():
            raise SupermarketPilotError(f"{name} must be a non-empty string")
    if payload.get("type") != "FeatureCollection":
        raise SupermarketPilotError("archived payload must be a GeoJSON FeatureCollection")
    if len(payload_sha256) != 64 or any(
        character not in "0123456789abcdef" for character in payload_sha256
    ):
        raise SupermarketPilotError("payload_sha256 must be a lowercase SHA-256 digest")
    features = payload.get("features")
    if not isinstance(features, list):
        raise SupermarketPilotError("archived payload features must be a list")
    assertions: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, feature in enumerate(features):
        if not isinstance(feature, Mapping):
            raise SupermarketPilotError("archived features must be objects")
        properties = feature.get("properties")
        if not isinstance(properties, Mapping):
            raise SupermarketPilotError("archived features require properties")
        premise_type = properties.get("Premise_Type")
        if not isinstance(premise_type, str) or "supermarket" not in premise_type.casefold():
            continue
        feature_id = feature.get("id")
        if feature_id is None:
            feature_id = properties.get("FID", index)
        assertion_id = f"{source_id}:{feature_id}"
        if assertion_id in seen:
            raise SupermarketPilotError("archived supermarket assertion identities must be unique")
        seen.add(assertion_id)
        assertion: dict[str, Any] = {
            "assertion_id": assertion_id,
            "source_id": source_id,
            "facility_type": "supermarket",
            "licence": licence,
            "observed_at": observed_at,
            "release_classification": "public",
            "source_premise_type": premise_type,
        }
        status = properties.get("Status")
        if isinstance(status, str) and status.strip():
            assertion["source_status"] = status.strip()
        geometry = feature.get("geometry")
        if isinstance(geometry, Mapping):
            assertion["geometry"] = dict(geometry)
        assertions.append(assertion)
    assertions.sort(key=lambda item: str(item["assertion_id"]))
    return {
        "record_type": "facility_assertions",
        "authoritative": False,
        "release_filter": "public-only",
        "registry_version": registry_version.strip(),
        "source_id": source_id.strip(),
        "payload_sha256": payload_sha256,
        "assertions": assertions,
        "claim_classification": "bounded-public-reference",
        "promotion_allowed": False,
        "nonclaims": [
            "Source premise classifications do not prove current operation or authority.",
            "The snapshot is not a complete or national supermarket registry.",
            "No live endpoint was contacted; callers must bind this output to an archived payload.",
        ],
    }


def _text(record: Mapping[str, Any], field: str) -> str:
    value = record.get(field)
    if not isinstance(value, str) or not value.strip():
        raise SupermarketPilotError(f"{field} must be a non-empty string")
    return value.strip()


def _number(
    record: Mapping[str, Any], field: str, *, positive: bool = False, non_negative: bool = False
) -> float:
    value = record.get(field)
    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not isfinite(float(value))
        or (positive and value <= 0)
        or (non_negative and value < 0)
    ):
        qualifier = (
            "finite and positive"
            if positive
            else ("finite and non-negative" if non_negative else "finite")
        )
        raise SupermarketPilotError(f"{field} must be {qualifier}")
    return float(value)


def build_access_health_reference(
    facility_snapshot: Mapping[str, Any],
    area_records: Sequence[Mapping[str, Any]],
    sensitivities: Sequence[Mapping[str, Any]],
    *,
    packet_id: str,
    generated_at: str,
) -> dict[str, Any]:
    """Bind public facility, access, context, and ecological-health evidence."""

    if not packet_id.strip() or not generated_at.strip():
        raise SupermarketPilotError("packet_id and generated_at must be non-empty")
    if (
        facility_snapshot.get("record_type") != "facility_assertions"
        or facility_snapshot.get("authoritative") is not False
        or facility_snapshot.get("release_filter") != "public-only"
    ):
        raise SupermarketPilotError("facility snapshot must be public-only and non-authoritative")
    registry_version = _text(facility_snapshot, "registry_version")
    assertions = facility_snapshot.get("assertions")
    if not isinstance(assertions, list) or not assertions:
        raise SupermarketPilotError("facility snapshot requires assertions")
    assertion_ids: list[str] = []
    for assertion in assertions:
        if not isinstance(assertion, Mapping):
            raise SupermarketPilotError("facility assertions must be objects")
        assertion_id = _text(assertion, "assertion_id")
        if assertion.get("facility_type") != "supermarket":
            raise SupermarketPilotError("facility assertions must be classified as supermarket")
        if assertion.get("release_classification", "public") != "public":
            raise SupermarketPilotError("facility snapshot contains a non-public assertion")
        for field in ("source_id", "licence", "observed_at"):
            _text(assertion, field)
        assertion_ids.append(assertion_id)
    if len(set(assertion_ids)) != len(assertion_ids):
        raise SupermarketPilotError("facility assertion identities must be unique")
    if not area_records:
        raise SupermarketPilotError("area records must be non-empty")

    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for area in area_records:
        if not isinstance(area, Mapping):
            raise SupermarketPilotError("area records must be objects")
        area_id = _text(area, "area_id")
        if area_id in seen:
            raise SupermarketPilotError("area identifiers must be unique")
        seen.add(area_id)
        measures = area.get("access_measures")
        context = area.get("context")
        health = area.get("health")
        if not all(isinstance(value, Mapping) for value in (measures, context, health)):
            raise SupermarketPilotError("access_measures, context and health must be objects")
        assert isinstance(measures, Mapping)
        assert isinstance(context, Mapping)
        assert isinstance(health, Mapping)
        normalized_measures = {
            field: _number(measures, field, non_negative=True) for field in _ACCESS_MEASURES
        }
        normalized_context = {field: _text(context, field) for field in _CONTEXT_FIELDS}
        if health.get("ecological") is not True:
            raise SupermarketPilotError("health records must be explicitly ecological")
        small_cell_status = _text(health, "small_cell_status")
        if small_cell_status not in {"eligible", "suppressed"}:
            raise SupermarketPilotError("small_cell_status must be eligible or suppressed")
        outcome = health.get("outcome_rate")
        if small_cell_status == "suppressed":
            if outcome is not None:
                raise SupermarketPilotError("suppressed health records must not expose a rate")
            outcome_rate = None
        else:
            outcome_rate = _number(health, "outcome_rate", non_negative=True)
        normalized_health = {
            "outcome_rate": outcome_rate,
            "denominator": _number(health, "denominator", positive=True),
            "source_ref": _text(health, "source_ref"),
            "ecological": True,
            "small_cell_status": small_cell_status,
        }
        normalized.append(
            {
                "area_id": area_id,
                "access_measures": normalized_measures,
                "context": normalized_context,
                "health": normalized_health,
            }
        )
    sensitivity_types = {
        item.get("record_type") for item in sensitivities if isinstance(item, Mapping)
    }
    if sensitivity_types != _SENSITIVITY_TYPES or len(sensitivities) != len(_SENSITIVITY_TYPES):
        raise SupermarketPilotError(
            "sensitivities must contain spatial confounding, MAUP and measurement error records"
        )
    for sensitivity in sensitivities:
        nonclaims = sensitivity.get("nonclaims")
        if not isinstance(nonclaims, list) or not nonclaims:
            raise SupermarketPilotError("sensitivity records must retain nonclaims")
    normalized.sort(key=lambda row: str(row["area_id"]))
    body: dict[str, Any] = {
        "schema_version": "1.0.0",
        "record_type": "supermarket_access_health_reference",
        "packet_id": packet_id.strip(),
        "generated_at": generated_at.strip(),
        "registry_version": registry_version,
        "facility_assertion_ids": sorted(assertion_ids),
        "areas": normalized,
        "sensitivities": sorted(
            [dict(item) for item in sensitivities], key=lambda item: str(item["record_type"])
        ),
        "constructs_kept_distinct": [
            "density",
            "accessibility",
            "capacity",
            "competition",
            "context",
            "ecological-health-association",
        ],
        "claim_classification": "bounded-descriptive-reference",
        "promotion_allowed": False,
        "nonclaims": [
            "Area-level associations do not support individual or causal interpretation.",
            "Public facility assertions are not an authoritative or complete supermarket registry.",
            "Reference measures do not establish affordability, food availability or access truth.",
        ],
    }
    body["packet_sha256"] = sha256_json(body)
    return body


def build_planning_alternatives_reference(
    feasibility_records: Sequence[Mapping[str, Any]],
    alternatives: Sequence[Mapping[str, Any]],
    *,
    packet_id: str,
    generated_at: str,
    non_modelled_constraints: Sequence[str],
) -> dict[str, Any]:
    """Bind cited planning dispositions to a complete bounded trade-off frontier."""

    if not packet_id.strip() or not generated_at.strip():
        raise SupermarketPilotError("packet_id and generated_at must be non-empty")
    if any(not isinstance(item, str) or not item.strip() for item in non_modelled_constraints):
        raise SupermarketPilotError("non-modelled constraints must be non-empty strings")
    constraints = tuple(sorted(set(non_modelled_constraints)))
    if _REQUIRED_NON_MODELLED.difference(constraints):
        raise SupermarketPilotError("market, land, community and consent constraints are required")
    if not feasibility_records:
        raise SupermarketPilotError("feasibility records must be non-empty")
    dispositions: list[dict[str, Any]] = []
    eligible: set[str] = set()
    seen: set[str] = set()
    for record in feasibility_records:
        if (
            not isinstance(record, Mapping)
            or record.get("record_type") != "planning-feasibility-query"
        ):
            raise SupermarketPilotError(
                "feasibility inputs must be planning-feasibility-query records"
            )
        candidate_id = _text(record, "feature_ref")
        if candidate_id in seen:
            raise SupermarketPilotError("planning candidate identities must be unique")
        seen.add(candidate_id)
        rules = record.get("rules")
        if (
            not isinstance(rules, list)
            or not rules
            or record.get("rules_sha256") != sha256_json(rules)
        ):
            raise SupermarketPilotError("planning feasibility rules require a valid digest")
        status = record.get("decision_status")
        if status not in {"permitted", "discretionary", "prohibited", "unresolved"}:
            raise SupermarketPilotError("planning feasibility decision_status is invalid")
        if (
            record.get("authority_required") is not True
            or record.get("promotion_allowed") is not False
        ):
            raise SupermarketPilotError(
                "planning feasibility must require authority and prohibit promotion"
            )
        if any(not isinstance(rule, Mapping) for rule in rules):
            raise SupermarketPilotError("planning feasibility rules must be objects")
        rule_statuses = {rule.get("status") for rule in rules}
        if not rule_statuses <= {"permitted", "discretionary", "prohibited", "unresolved"}:
            raise SupermarketPilotError("cited planning rule status is invalid")
        if "unresolved" in rule_statuses or (
            "prohibited" in rule_statuses and rule_statuses - {"prohibited"}
        ):
            derived_status = "unresolved"
        elif "prohibited" in rule_statuses:
            derived_status = "prohibited"
        elif "discretionary" in rule_statuses:
            derived_status = "discretionary"
        else:
            derived_status = "permitted"
        if status != derived_status:
            raise SupermarketPilotError("planning decision_status does not match cited rules")
        if status in {"permitted", "discretionary"}:
            eligible.add(candidate_id)
        dispositions.append(
            {
                "candidate_id": candidate_id,
                "decision_status": status,
                "rules_sha256": record["rules_sha256"],
                "authority_required": True,
            }
        )
    if not alternatives or any(not isinstance(item, Mapping) for item in alternatives):
        raise SupermarketPilotError("alternatives must be non-empty objects")
    alternative_ids = {str(item.get("candidate_id", "")) for item in alternatives}
    if not alternative_ids or alternative_ids - eligible:
        raise SupermarketPilotError(
            "alternatives must use only permitted or discretionary candidates"
        )
    for alternative in alternatives:
        metrics = alternative.get("metrics")
        if not isinstance(metrics, Mapping) or set(metrics) != set(_ALTERNATIVE_METRICS):
            raise SupermarketPilotError("alternatives require the complete trade-off metric set")
        if any(
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not isfinite(float(value))
            or value < 0
            for value in metrics.values()
        ):
            raise SupermarketPilotError("alternative metrics must be finite and non-negative")
    pareto = build_service_pareto_report(
        alternatives,
        maximize=("capacity_served", "competition_balance"),
        minimize=(
            "average_access",
            "worst_case_access",
            "subgroup_gap",
            "cost",
            "robustness_loss",
        ),
        non_modelled_constraints=constraints,
    )
    body: dict[str, Any] = {
        "schema_version": "1.0.0",
        "record_type": "supermarket_planning_alternatives_reference",
        "packet_id": packet_id.strip(),
        "generated_at": generated_at.strip(),
        "planning_dispositions": sorted(dispositions, key=lambda item: item["candidate_id"]),
        "pareto": pareto,
        "candidate_status": "bounded-cited-reference",
        "promotion_allowed": False,
        "nonclaims": [
            "Cited planning status is not legal advice, consent certainty or land availability.",
            (
                "Pareto membership is not a preferred site, commercial recommendation "
                "or authority decision."
            ),
            "Market, land, community and consent constraints remain outside the model.",
        ],
    }
    body["packet_sha256"] = sha256_json(body)
    return body
