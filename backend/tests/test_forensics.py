from datetime import datetime, timezone

from app.domain.events.models import CanonicalEvent
from app.domain.events.types import (
    EventRelationshipType,
    EventSeverity,
    EventStatus,
    EventType,
)


def make_event(
    event_id: str = "evt-test",
    event_type: EventType = EventType.TOOL_CALL,
    *,
    status: EventStatus = EventStatus.RECEIVED,
    details: dict | None = None,
    metadata: dict | None = None,
) -> CanonicalEvent:
    return CanonicalEvent(
        event_id=event_id,
        timestamp=datetime.now(timezone.utc),
        session_id="session-test",
        agent_id="agent-test",
        provider="test",
        event_type=event_type,
        status=status,
        severity=EventSeverity.LOW,
        details=details or {},
        metadata=metadata or {},
    )


def test_event_relationship_ids():
    event = CanonicalEvent(
        event_id="evt-child",
        timestamp=datetime.now(timezone.utc),
        session_id="session-test",
        agent_id="agent-test",
        provider="test",
        event_type=EventType.TOOL_CALL,
        status=EventStatus.RECEIVED,
        severity=EventSeverity.LOW,
        parent_event_id="evt-parent",
        related_event_id="evt-related",
    )

    relationships = event.relationship_ids()

    assert (
        "evt-parent",
        EventRelationshipType.PARENT,
    ) in relationships

    assert (
        "evt-related",
        EventRelationshipType.RELATED,
    ) in relationships


def test_security_event_detection():
    event = make_event(
        event_type=EventType.PROMPT_INJECTION_DETECTED,
    )

    assert event.is_security_event is True
    assert event.is_policy_violation is False


def test_sensitive_action_detection():
    event = make_event(
        event_type=EventType.SENSITIVE_ACTION_ATTEMPTED,
    )

    assert event.is_sensitive_action is True


def test_blocked_event_detection():
    event = make_event(
        event_type=EventType.TOOL_BLOCKED,
        status=EventStatus.BLOCKED,
    )

    assert event.is_blocked is True


def test_policy_violation_detection():
    event = make_event(
        event_type=EventType.POLICY_VIOLATION,
    )

    assert event.is_security_event is True
    assert event.is_policy_violation is True
