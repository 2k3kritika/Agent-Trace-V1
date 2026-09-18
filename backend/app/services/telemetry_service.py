from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from app.infrastructure.postgres.models import Event
from app.repositories.interfaces import EventRepository
from app.schemas.telemetry import (
    TelemetryBatchRequest,
    TelemetryBatchResponse,
    TelemetryEventRequest,
    TelemetryIngestResponse,
)
from app.services.event_service import EventService


class TelemetryService:
    """
    Entry point for telemetry ingestion.

    HTTP/API layers should call this service rather than interacting
    directly with repositories.
    """

    def __init__(
        self,
        event_service: EventService,
    ) -> None:
        self.event_service = event_service

    async def ingest_event(
        self,
        request: TelemetryEventRequest,
    ) -> TelemetryIngestResponse:
        payload = self._request_to_payload(request)

        event, created = await self.event_service.ingest(
            payload,
            provider=request.provider,
            default_agent_id=request.agent_id,
            default_session_id=request.session_id,
        )

        return TelemetryIngestResponse(
            event_id=event.event_id,
            accepted=True,
            duplicate=not created,
        )

    async def ingest_batch(
        self,
        request: TelemetryBatchRequest,
    ) -> TelemetryBatchResponse:
        payloads = [
            self._request_to_payload(event_request)
            for event_request in request.events
        ]

        events, duplicate_count = (
            await self.event_service.ingest_many(
                payloads,
                provider=request.provider,
                default_agent_id=request.agent_id,
                default_session_id=request.session_id,
            )
        )

        return TelemetryBatchResponse(
            accepted=len(events),
            duplicates=duplicate_count,
            event_ids=[
                event.event_id
                for event in events
            ],
        )

    @staticmethod
    def _request_to_payload(
        request: TelemetryEventRequest,
    ) -> Mapping[str, Any]:
        payload = request.model_dump(
            mode="json",
            exclude_none=True,
        )

        return payload