from datetime import datetime, timezone

import pytest

from app.domain.events.normalizer import (
    EventNormalizationError,
    EventNormalizer,
)
from app.domain.events.types import (
    EventSeverity,
    EventStatus,
    EventType,
)


def test_normalizes_basic_event():
    payload = {
        "event_id": "evt-001",
        "agent_id": "agent-001",
        "session_id": "session-001",
        "event_type": "PROMPT_INJECTION_DETECTED",
        "status": "ATTEMPTED",
        "severity": "HIGH",
        "timestamp": "2026-09-18T10:00:00+00:00",
        "details": {
            "message": "Ignore previous instructions",
        },
    }

    event = EventNormalizer().normalize(payload)

    assert event.event_id == "evt-001"
    assert event.agent_id == "agent-001"
    assert event.session_id == "session-001"
    assert event.provider == "unknown"

    assert event.event_type == EventType.PROMPT_INJECTION_DETECTED
    assert event.status == EventStatus.ATTEMPTED
    assert event.severity == EventSeverity.HIGH

    assert event.timestamp.tzinfo is not None
    assert event.details["message"] == "Ignore previous instructions"


def test_normalizes_naive_timestamp():
    payload = {
        "event_id": "evt-002",
        "agent_id": "agent-002",
        "event_type": "TOOL_CALL",
        "timestamp": datetime(2026, 9, 18, 10, 0, 0),
    }

    event = EventNormalizer().normalize(payload)

    assert event.timestamp.tzinfo == timezone.utc
    assert event.session_id == "unknown-session"
    assert event.provider == "unknown"
    assert event.event_type == EventType.TOOL_CALL


def test_missing_event_id_raises():
    payload = {
        "agent_id": "agent-001",
        "event_type": "TOOL_CALL",
    }

    with pytest.raises(EventNormalizationError):
        EventNormalizer().normalize(payload)


def test_missing_agent_id_raises():
    payload = {
        "event_id": "evt-001",
        "event_type": "TOOL_CALL",
    }

    with pytest.raises(EventNormalizationError):
        EventNormalizer().normalize(payload)


def test_normalize_many():
    payloads = [
        {
            "event_id": "evt-001",
            "agent_id": "agent-001",
            "event_type": "AGENT_STARTED",
        },
        {
            "event_id": "evt-002",
            "agent_id": "agent-001",
            "event_type": "TOOL_CALL",
        },
    ]

    events = EventNormalizer().normalize_many(payloads)

    assert len(events) == 2
    assert events[0].event_id == "evt-001"
    assert events[1].event_id == "evt-002"

    assert all(event.provider == "unknown" for event in events)
    assert all(event.session_id == "unknown-session" for event in events)


def test_provider_and_session_defaults_can_be_supplied():
    payload = {
        "event_id": "evt-003",
        "agent_id": "agent-003",
        "event_type": "AGENT_STARTED",
    }

    event = EventNormalizer().normalize(
        payload,
        provider="gemini",
        default_session_id="session-003",
    )

    assert event.provider == "gemini"
    assert event.session_id == "session-003"


def test_payload_provider_takes_precedence():
    payload = {
        "event_id": "evt-004",
        "agent_id": "agent-004",
        "provider": "payload-provider",
        "event_type": "AGENT_STARTED",
    }

    event = EventNormalizer().normalize(
        payload,
        provider="fallback-provider",
    )

    assert event.provider == "payload-provider"