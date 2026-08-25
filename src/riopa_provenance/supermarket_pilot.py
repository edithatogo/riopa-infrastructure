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


def _text(record: Mapping[str, Any], field: str) -> str:
    value = record.get(field)
    if not isinstance(value, str) or not value.strip():
        raise SupermarketPilotError(f"{field} must be a non-empty string")
    return value.strip()


def _number(record: Mapping[str, Any], field: str, *, positive: bool = False) -> float:
    value = record.get(field)
    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not isfinite(float(value))
        or (positive and value <= 0)
    ):
        qualifier = "finite and positive" if positive else "finite"
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
        normalized_measures = {field: _number(measures, field) for field in _ACCESS_MEASURES}
        normalized_context = {field: _text(context, field) for field in _CONTEXT_FIELDS}
        if health.get("ecological") is not True:
            raise SupermarketPilotError("health records must be explicitly ecological")
        normalized_health = {
            "outcome_rate": _number(health, "outcome_rate"),
            "denominator": _number(health, "denominator", positive=True),
            "source_ref": _text(health, "source_ref"),
            "ecological": True,
            "small_cell_status": _text(health, "small_cell_status"),
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
    constraints = tuple(sorted(set(non_modelled_constraints)))
    if any(not isinstance(item, str) or not item.strip() for item in constraints):
        raise SupermarketPilotError("non-modelled constraints must be non-empty strings")
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
    alternative_ids = {str(item.get("candidate_id", "")) for item in alternatives}
    if not alternative_ids or alternative_ids - eligible:
        raise SupermarketPilotError(
            "alternatives must use only permitted or discretionary candidates"
        )
    for alternative in alternatives:
        metrics = alternative.get("metrics")
        if not isinstance(metrics, Mapping) or set(metrics) != set(_ALTERNATIVE_METRICS):
            raise SupermarketPilotError("alternatives require the complete trade-off metric set")
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
