from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.adapters.base import AdapterConnectionResult, AdapterHealthResult
from app.adapters.registry import AdapterRegistry
from app.domain.events.models import CanonicalEvent
from app.services.event_service import EventService


class AdapterService:
    """
    Application service for provider-specific telemetry adapters.

    Responsibilities:
    1. Resolve an adapter.
    2. Normalize provider-specific telemetry.
    3. Pass canonical events into EventService.
    4. Keep routes independent from repositories and adapter internals.
    """

    def __init__(
        self,
        registry: AdapterRegistry,
        event_service: EventService,
    ) -> None:
        self.registry = registry
        self.event_service = event_service

    def list_adapters(self) -> list[str]:
        return self.registry.list_adapters()

    def get_adapter(self, adapter_name: str):
        return self.registry.get(adapter_name)

    def normalize_event(
        self,
        adapter_name: str,
        raw_event: Mapping[str, Any],
        *,
        default_agent_id: str | None = None,
        default_session_id: str | None = None,
    ) -> CanonicalEvent:
        adapter = self.registry.get(adapter_name)

        return adapter.normalize_event(
            raw_event,
            default_agent_id=default_agent_id,
            default_session_id=default_session_id,
        )

    async def ingest_event(
        self,
        adapter_name: str,
        raw_event: Mapping[str, Any],
        *,
        default_agent_id: str | None = None,
        default_session_id: str | None = None,
    ):
        canonical_event = self.normalize_event(
            adapter_name,
            raw_event,
            default_agent_id=default_agent_id,
            default_session_id=default_session_id,
        )

        return await self.event_service.ingest_event(canonical_event)

    async def ingest_events(
        self,
        adapter_name: str,
        raw_events: list[Mapping[str, Any]],
        *,
        default_agent_id: str | None = None,
        default_session_id: str | None = None,
    ) -> list[Any]:
        results: list[Any] = []

        for raw_event in raw_events:
            result = await self.ingest_event(
                adapter_name,
                raw_event,
                default_agent_id=default_agent_id,
                default_session_id=default_session_id,
            )
            results.append(result)

        return results

    def validate_connection(
        self,
        adapter_name: str,
        configuration: Mapping[str, Any] | None = None,
    ) -> AdapterConnectionResult:
        adapter = self.registry.get(adapter_name)
        return adapter.validate_connection(configuration)

    def health_check(self, adapter_name: str) -> AdapterHealthResult:
        adapter = self.registry.get(adapter_name)
        return adapter.health_check()