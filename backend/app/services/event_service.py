from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any

from app.domain.events.models import CanonicalEvent
from app.domain.events.normalizer import (
    EventNormalizationError,
    EventNormalizer,
)
from app.domain.events.types import EventSeverity
from app.infrastructure.postgres.models import Event
from app.repositories.interfaces import (
    EventRepository,
    RepositoryListResult,
)


class EventServiceError(Exception):
    """Base exception for event service failures."""


class EventService:
    """
    Application service responsible for canonical event ingestion.

    The service owns orchestration and conversion between domain events
    and persistence models. It deliberately does not perform SQL queries.
    """

    def __init__(
        self,
        event_repository: EventRepository,
        normalizer: EventNormalizer | None = None,
    ) -> None:
        self.event_repository = event_repository
        self.normalizer = normalizer or EventNormalizer()

    async def ingest(
        self,
        payload: Mapping[str, Any],
        *,
        provider: str | None = None,
        default_agent_id: str | None = None,
        default_session_id: str | None = None,
    ) -> tuple[Event, bool]:
        """
        Normalize and persist a single telemetry event.

        Returns:
            (event, created)

        `created=False` means the event already existed and was treated
        as an idempotent duplicate.
        """

        try:
            canonical = self.normalizer.normalize(
                payload,
                provider=provider,
                default_agent_id=default_agent_id,
                default_session_id=default_session_id,
            )
        except EventNormalizationError as exc:
            raise EventServiceError(
                f"Event normalization failed: {exc}"
            ) from exc

        persistence_model = self._to_persistence_model(canonical)

        return await self.event_repository.create_unique(
            persistence_model
        )

    async def ingest_many(
        self,
        payloads: Sequence[Mapping[str, Any]],
        *,
        provider: str | None = None,
        default_agent_id: str | None = None,
        default_session_id: str | None = None,
    ) -> tuple[list[Event], int]:
        """
        Normalize and persist a batch of telemetry events.

        Returns:
            (events, duplicate_count)
        """

        events: list[Event] = []
        duplicate_count = 0

        for payload in payloads:
            event, created = await self.ingest(
                payload,
                provider=provider,
                default_agent_id=default_agent_id,
                default_session_id=default_session_id,
            )

            events.append(event)

            if not created:
                duplicate_count += 1

        return events, duplicate_count

    async def get_event(
        self,
        event_id: str,
    ) -> Event:
        return await self.event_repository.get_by_event_id(
            event_id
        )

    async def list_events(
        self,
        *,
        page: int = 1,
        page_size: int = 25,
        session_id: str | None = None,
        agent_id: str | None = None,
        event_type: str | None = None,
        severity: str | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> RepositoryListResult[Event]:
        return await self.event_repository.list(
            page=page,
            page_size=page_size,
            session_id=session_id,
            agent_id=agent_id,
            event_type=event_type,
            severity=severity,
            status=status,
            search=search,
        )

    async def list_session_events(
        self,
        session_id: str,
        *,
        page: int = 1,
        page_size: int = 100,
    ) -> RepositoryListResult[Event]:
        return await self.event_repository.list_session_events(
            session_id,
            page=page,
            page_size=page_size,
        )

    async def list_security_events(
        self,
        *,
        session_id: str | None = None,
        page: int = 1,
        page_size: int = 100,
    ) -> RepositoryListResult[Event]:
        return await self.event_repository.list_security_events(
            session_id=session_id,
            page=page,
            page_size=page_size,
        )

    @staticmethod
    def _to_persistence_model(
        event: CanonicalEvent,
    ) -> Event:
        return Event(
            event_id=event.event_id,
            timestamp=event.timestamp,
            session_id=event.session_id,
            agent_id=event.agent_id,
            provider=event.provider,
            event_type=event.event_type.value,
            status=event.status.value,
            tool=event.tool,
            source=event.source,
            severity=event.severity.value,
            details=dict(event.details),
            metadata=dict(event.metadata),
            parent_event_id=event.parent_event_id,
            related_event_id=event.related_event_id,
            trace_id=event.trace_id,
            span_id=event.span_id,
        )