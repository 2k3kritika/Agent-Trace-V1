from __future__ import annotations

from datetime import datetime
from typing import Any

from app.domain.events.models import CanonicalEvent
from app.domain.events.normalizer import EventNormalizer
from app.domain.events.types import EventSeverity
from app.infrastructure.postgres.models import Event
from app.repositories.interfaces import EventRepository
from app.schemas.common import PaginationParams
from app.schemas.events import (
    CanonicalEventResponse,
    EventListResponse,
)


class EventService:
    def __init__(
        self,
        repository: EventRepository,
        normalizer: EventNormalizer | None = None,
    ):
        self.repository = repository
        self.normalizer = normalizer or EventNormalizer()

    @staticmethod
    def _to_response(event: Event) -> CanonicalEventResponse:
        return CanonicalEventResponse.model_validate(
            {
                "event_id": event.event_id,
                "timestamp": event.timestamp,
                "session_id": event.session_id,
                "agent_id": event.agent_id,
                "provider": event.provider,
                "event_type": event.event_type,
                "status": event.status,
                "severity": event.severity,
                "tool": event.tool,
                "source": event.source,
                "details": event.details or {},
                "metadata": event.metadata or {},
                "parent_event_id": event.parent_event_id,
                "related_event_id": event.related_event_id,
                "trace_id": event.trace_id,
                "span_id": event.span_id,
            }
        )

    @staticmethod
    def _to_model(event: CanonicalEvent) -> Event:
        return Event(
            event_id=event.event_id,
            timestamp=event.timestamp,
            session_id=event.session_id,
            agent_id=event.agent_id,
            provider=event.provider,
            event_type=event.event_type.value,
            status=event.status.value,
            severity=event.severity.value,
            tool=event.tool,
            source=event.source,
            details=event.details,
            metadata=event.metadata,
            parent_event_id=event.parent_event_id,
            related_event_id=event.related_event_id,
            trace_id=event.trace_id,
            span_id=event.span_id,
        )

    async def ingest_event(
        self,
        event: CanonicalEvent,
        *,
        allow_duplicate: bool = False,
    ) -> CanonicalEventResponse:
        persistence_model = self._to_model(event)

        if allow_duplicate:
            created = await self.repository.create(persistence_model)
        else:
            created = await self.repository.create_unique(
                persistence_model
            )

        return self._to_response(created)

    async def normalize_and_ingest(
        self,
        payload: dict[str, Any],
        *,
        default_agent_id: str | None = None,
        default_session_id: str | None = None,
        default_provider: str | None = None,
    ) -> CanonicalEventResponse:
        canonical_event = self.normalizer.normalize(
            payload,
            default_agent_id=default_agent_id,
            default_session_id=default_session_id,
            default_provider=default_provider,
        )

        return await self.ingest_event(canonical_event)

    async def get_event(
        self,
        event_id: str,
    ) -> CanonicalEventResponse | None:
        event = await self.repository.get_by_id(event_id)

        if event is None:
            return None

        return self._to_response(event)

    async def list_events(
        self,
        pagination: PaginationParams,
        *,
        session_id: str | None = None,
        agent_id: str | None = None,
        event_type: str | None = None,
        severity: EventSeverity | None = None,
        from_timestamp: datetime | None = None,
        to_timestamp: datetime | None = None,
        search: str | None = None,
    ) -> EventListResponse:
        result = await self.repository.list_page(
            page=pagination.page,
            page_size=pagination.page_size,
            session_id=session_id,
            agent_id=agent_id,
            event_type=event_type,
            severity=severity.value if severity else None,
            from_timestamp=from_timestamp,
            to_timestamp=to_timestamp,
            search=search,
        )

        items = [
            self._to_response(event)
            for event in result.items
        ]

        return EventListResponse(
            items=items,
            page=pagination.page,
            page_size=pagination.page_size,
            total=result.total,
            has_next=(
                pagination.page * pagination.page_size
                < result.total
            ),
        )

    async def list_session_events(
        self,
        session_id: str,
    ) -> list[CanonicalEventResponse]:
        result = await self.repository.list_session_events(
            session_id
        )

        return [
            self._to_response(event)
            for event in result
        ]

    async def list_security_events(
        self,
        pagination: PaginationParams,
    ) -> EventListResponse:
        result = await self.repository.list_security_events(
            page=pagination.page,
            page_size=pagination.page_size,
        )

        items = [
            self._to_response(event)
            for event in result.items
        ]

        return EventListResponse(
            items=items,
            page=pagination.page,
            page_size=pagination.page_size,
            total=result.total,
            has_next=(
                pagination.page * pagination.page_size
                < result.total
            ),
        )