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
        # Normalize timestamp.
        if self.timestamp.tzinfo is None:
            self.timestamp = self.timestamp.replace(tzinfo=timezone.utc)

        # Normalize required strings.
        self.event_id = self.event_id.strip()
        self.session_id = self.session_id.strip()
        self.agent_id = self.agent_id.strip()
        self.provider = self.provider.strip()

        # Normalize enum-like values into their actual enum types.
        #
        # This is important because the rest of the domain layer expects
        # EventType/EventStatus/EventSeverity instances and accesses .value.
        if isinstance(self.event_type, str):
            try:
                self.event_type = EventType(self.event_type.strip().upper())
            except ValueError:
                # Preserve unknown/custom event types as strings.
                self.event_type = self.event_type.strip().upper()

        if isinstance(self.status, str):
            try:
                self.status = EventStatus(self.status.strip().upper())
            except ValueError:
                # Preserve unknown/custom statuses as strings.
                self.status = self.status.strip().upper()

        if isinstance(self.severity, str):
            try:
                self.severity = EventSeverity(self.severity.strip().upper())
            except ValueError:
                # Preserve unknown/custom severity values as strings.
                self.severity = self.severity.strip().upper()

    @property
    def is_security_event(self) -> bool:
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
        return self.event_type == EventType.SENSITIVE_ACTION_ATTEMPTED

    @property
    def is_blocked(self) -> bool:
        return (
            self.event_type == EventType.TOOL_BLOCKED
            or self.status == EventStatus.BLOCKED
        )

    @property
    def is_policy_violation(self) -> bool:
        return self.event_type == EventType.POLICY_VIOLATION

    def relationship_ids(
        self,
    ) -> list[tuple[str, EventRelationshipType]]:
        """
        Return explicit event relationships.

        Each relationship is represented as:
            (event_id, relationship_type)
        """

        relationships: list[
            tuple[str, EventRelationshipType]
        ] = []

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