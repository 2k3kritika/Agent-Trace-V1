"""PostgreSQL repository for canonical telemetry events."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import select

from app.domain.events.types import EventType
from app.infrastructure.postgres.models import Event
from app.core.exceptions import DuplicateResourceError
from app.repositories.interfaces import (
    EventRepository,
)
from app.core.exceptions import NotFoundError
from app.repositories.postgres.base import PostgresRepository


class PostgresEventRepository(
    PostgresRepository[Event],
    EventRepository,
):
    """PostgreSQL implementation of EventRepository."""

    model = Event

    async def get_by_event_id(self, event_id: str) -> Event:
        """Retrieve an event using its canonical event ID."""
        result = await self.session.execute(
            select(Event).where(Event.event_id == event_id)
        )

        event = result.scalar_one_or_none()

        if event is None:
            raise NotFoundError(
                f"Event with event_id '{event_id}' was not found."
            )

        return event

    async def get_optional_by_event_id(
        self,
        event_id: str,
    ) -> Event | None:
        """Retrieve an event or return None."""
        result = await self.session.execute(
            select(Event).where(Event.event_id == event_id)
        )

        return result.scalar_one_or_none()

    async def create_unique(self, entity: Event) -> Event:
        """Create an event while enforcing event-level idempotency."""
        existing = await self.get_optional_by_event_id(entity.event_id)

        if existing is not None:
            raise DuplicateResourceError(
                f"Event with event_id '{entity.event_id}' already exists."
            )

        return await self.create(entity)

    async def list_events(
        self,
        *,
        page: int,
        page_size: int,
        session_id: str | None = None,
        agent_id: str | None = None,
        event_type: str | EventType | None = None,
        severity: str | None = None,
        from_timestamp: datetime | None = None,
        to_timestamp: datetime | None = None,
        search: str | None = None,
    ) -> tuple[list[Event], int]:
        """List events with investigation-oriented filters."""
        statement = select(Event)

        if session_id:
            statement = statement.where(Event.session_id == session_id)

        if agent_id:
            statement = statement.where(Event.agent_id == agent_id)

        if event_type:
            normalized_event_type = (
                event_type.value
                if isinstance(event_type, EventType)
                else event_type
            )
            statement = statement.where(
                Event.event_type == normalized_event_type
            )

        if severity:
            statement = statement.where(Event.severity == severity)

        if from_timestamp:
            statement = statement.where(Event.timestamp >= from_timestamp)

        if to_timestamp:
            statement = statement.where(Event.timestamp <= to_timestamp)

        if search:
            pattern = f"%{search.strip()}%"
            statement = statement.where(
                Event.event_id.ilike(pattern)
                | Event.tool.ilike(pattern)
                | Event.source.ilike(pattern)
                | Event.event_type.ilike(pattern)
            )

        statement = statement.order_by(
            Event.timestamp.desc(),
        )

        return await self.list_page(
            page=page,
            page_size=page_size,
            statement=statement,
        )

    async def list_session_events(
        self,
        session_id: str,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[Event], int]:
        """Return events belonging to one session."""
        statement = (
            select(Event)
            .where(Event.session_id == session_id)
            .order_by(Event.timestamp.asc())
        )

        return await self.list_page(
            page=page,
            page_size=page_size,
            statement=statement,
        )

    async def list_security_events(
        self,
        session_id: str,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[Event], int]:
        """Return security-relevant events for a session."""
        security_types = [
            EventType.UNTRUSTED_CONTENT.value,
            EventType.PROMPT_INJECTION_DETECTED.value,
            EventType.SENSITIVE_ACTION_ATTEMPTED.value,
            EventType.POLICY_EVALUATION.value,
            EventType.POLICY_VIOLATION.value,
            EventType.TOOL_BLOCKED.value,
        ]

        statement = (
            select(Event)
            .where(
                Event.session_id == session_id,
                Event.event_type.in_(security_types),
            )
            .order_by(Event.timestamp.asc())
        )

        return await self.list_page(
            page=page,
            page_size=page_size,
            statement=statement,
        )