"""
Domain models for canonical AgentTrace events.

These models contain no SQLAlchemy or database-specific behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.domain.events.types import (
    EventRelationshipType,
    EventSeverity,
    EventStatus,
    EventType,
)


@dataclass(slots=True)
class CanonicalEvent:
    """
    Provider-neutral AgentTrace event.

    Every supported adapter should ultimately produce this structure.
    """

    event_id: str
    timestamp: datetime

    session_id: str
    agent_id: str
    provider: str

    event_type: EventType | str
    status: EventStatus | str

    tool: str | None = None
    source: str | None = None
    severity: EventSeverity | str | None = None

    details: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    parent_event_id: str | None = None
    related_event_id: str | None = None

    trace_id: str | None = None
    span_id: str | None = None

    def __post_init__(self) -> None:
        """Normalize timestamps and enum-like string values."""

        if self.timestamp.tzinfo is None:
            self.timestamp = self.timestamp.replace(
                tzinfo=timezone.utc,
            )

        self.event_id = self.event_id.strip()
        self.session_id = self.session_id.strip()
        self.agent_id = self.agent_id.strip()
        self.provider = self.provider.strip()

        if isinstance(self.event_type, str):
            self.event_type = self.event_type.strip().upper()

        if isinstance(self.status, str):
            self.status = self.status.strip().upper()

        if isinstance(self.severity, str):
            self.severity = self.severity.strip().upper()

    @property
    def is_security_event(self) -> bool:
        """Return whether this event represents a security-relevant action."""

        security_events = {
            EventType.UNTRUSTED_CONTENT,
            EventType.PROMPT_INJECTION_DETECTED,
            EventType.SENSITIVE_ACTION_ATTEMPTED,
            EventType.POLICY_EVALUATION,
            EventType.POLICY_VIOLATION,
            EventType.TOOL_BLOCKED,
            EventType.ERROR,
        }

        return self.event_type in security_events

    @property
    def is_sensitive_action(self) -> bool:
        """Return whether this event represents a sensitive action attempt."""

        return self.event_type == EventType.SENSITIVE_ACTION_ATTEMPTED

    @property
    def is_blocked(self) -> bool:
        """Return whether the event represents a blocked action."""

        return (
            self.event_type == EventType.TOOL_BLOCKED
            or self.status == EventStatus.BLOCKED
        )

    @property
    def is_policy_violation(self) -> bool:
        """Return whether the event represents a policy violation."""

        return self.event_type == EventType.POLICY_VIOLATION

    def relationship_ids(self) -> list[tuple[str, EventRelationshipType]]:
        """
        Return explicitly declared relationships for this event.
        """

        relationships: list[tuple[str, EventRelationshipType]] = []

        if self.parent_event_id:
            relationships.append(
                (
                    self.parent_event_id,
                    EventRelationshipType.PARENT,
                )
            )

        if self.related_event_id:
            relationships.append(
                (
                    self.related_event_id,
                    EventRelationshipType.RELATED,
                )
            )

        return relationships


@dataclass(slots=True)
class EventRelationship:
    """Explicit relationship between two canonical events."""

    source_event_id: str
    target_event_id: str
    relationship_type: EventRelationshipType | str

    def __post_init__(self) -> None:
        if isinstance(self.relationship_type, str):
            self.relationship_type = self.relationship_type.strip().upper()


@dataclass(slots=True)
class EventCollection:
    """Ordered collection of canonical events for processing."""

    events: list[CanonicalEvent] = field(default_factory=list)

    def add(self, event: CanonicalEvent) -> None:
        """Add an event to the collection."""

        self.events.append(event)

    def sorted(self) -> list[CanonicalEvent]:
        """Return events ordered chronologically."""

        return sorted(
            self.events,
            key=lambda event: event.timestamp,
        )

    def for_session(self, session_id: str) -> list[CanonicalEvent]:
        """Return events belonging to a specific session."""

        return [
            event
            for event in self.events
            if event.session_id == session_id
        ]

    def for_agent(self, agent_id: str) -> list[CanonicalEvent]:
        """Return events belonging to a specific agent."""

        return [
            event
            for event in self.events
            if event.agent_id == agent_id
        ]