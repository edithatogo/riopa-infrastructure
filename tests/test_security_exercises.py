import pytest

from riopa_provenance.security_exercises import (
    SecurityExerciseError,
    build_exercise_packet,
    validate_exercise_execution,
    validate_exercise_packet,
)


def test_security_exercise_packet_is_secret_free_and_scenario_bound() -> None:
    packet = build_exercise_packet("malicious-input", source_revision="a" * 40)
    assert packet["status"] == "planned"
    assert packet["credential_material"] == "absent"
    assert validate_exercise_packet(packet) == ()


def test_security_exercise_packet_rejects_drift_and_credentials() -> None:
    packet = build_exercise_packet("rollback", source_revision="a" * 40)
    packet["required_controls"] = ["revoke"]
    packet["api_key"] = "must-not-be-recorded"
    errors = validate_exercise_packet(packet)
    assert any("required_controls" in error for error in errors)
    assert any("credential-shaped" in error for error in errors)
    with pytest.raises(SecurityExerciseError, match="unsupported"):
        build_exercise_packet("unknown", source_revision="a" * 40)


def test_execution_report_binds_controls_and_environment() -> None:
    report = {
        "exercise_id": "security-exercise-1",
        "scenario": "rollback",
        "source_revision": "a" * 40,
        "status": "executed",
        "environment": "hosted",
        "hosted_run_id": "32724264855",
        "controls": {
            "verify-fixity": "passed",
            "restore-predecessor": "passed",
            "record-receipt": "passed",
            "revoke": "passed",
        },
        "raw_log_sha256": "b" * 64,
        "non_assertive": True,
    }
    assert validate_exercise_execution(report) == ()


def test_failed_execution_requires_reason_and_preserves_non_assertive_boundary() -> None:
    report = {
        "exercise_id": "security-exercise-2",
        "scenario": "malicious-input",
        "source_revision": "a" * 40,
        "status": "failed",
        "environment": "local",
        "controls": {
            "quarantine": "failed",
            "validate": "not-run",
            "preserve-failure": "not-run",
            "notify": "not-run",
        },
        "raw_log_sha256": "c" * 64,
        "non_assertive": True,
    }
    errors = validate_exercise_execution(report)
    assert any("failure_reason" in error for error in errors)
