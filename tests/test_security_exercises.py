import pytest

from riopa_provenance.security_exercises import (
    SecurityExerciseError,
    build_exercise_packet,
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
