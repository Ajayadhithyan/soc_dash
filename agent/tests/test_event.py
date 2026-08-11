"""Tests for the normalized event schema."""

import pytest

from agent.event import (
    EVENT_REQUIRED_FIELDS,
    EventError,
    build_event,
    sanitize_event,
    validate_event,
)


def test_build_event_has_all_required_fields():
    event = build_event(
        event_type="PROCESS_STARTED",
        category="PROCESS",
        metadata={"pid": 42},
        user="alice",
        raw_log="Process started",
    )
    for field in EVENT_REQUIRED_FIELDS:
        assert field in event, f"missing required field: {field}"
    assert event["metadata"] == {"pid": 42}
    assert event["metadata"] == {"pid": 42}
    assert event["severity"] == "LOW"
    assert event["user"] == "alice"
    assert event["timestamp"]


def test_build_event_defaults():
    event = build_event(event_type="LOGIN_SUCCESS", category="LOGIN")
    assert event["src_ip"] == "0.0.0.0"
    assert event["dest_ip"] == "0.0.0.0"
    assert event["user"] == "unknown"


def test_build_event_rejects_bad_inputs():
    with pytest.raises(EventError):
        build_event(event_type="", category="PROCESS")
    with pytest.raises(EventError):
        build_event(event_type="X", category="")
    with pytest.raises(EventError):
        build_event(event_type="X", category="PROCESS", severity="HARDCORE")


def test_validate_event_roundtrip():
    event = build_event(event_type="NETWORK_CONNECTION", category="NETWORK")
    validate_event(event)  # must not raise


def test_validate_event_rejects_missing_category():
    event = build_event(event_type="X", category="PROCESS")
    del event["category"]
    with pytest.raises(EventError):
        validate_event(event)


def test_sanitize_event_removes_non_serializable():
    class Weird:
        pass

    event = build_event(event_type="X", category="PROCESS", metadata={"obj": Weird()})
    clean = sanitize_event(event)
    assert isinstance(clean["metadata"]["obj"], str)