from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from app.domain.events.models import CanonicalEvent


@dataclass(slots=True)
class AdapterConnectionResult:
    connected: bool
    adapter_name: str
    provider_name: str
    message: str
    metadata: dict[str, Any]


@dataclass(slots=True)
class AdapterHealthResult:
    healthy: bool
    adapter_name: str
    provider_name: str
    message: str
    metadata: dict[str, Any]


class AgentAdapter(ABC):
    """
    Provider-neutral adapter contract.

    Adapters translate provider-specific telemetry into the
    canonical AgentTrace event model.

    The adapter answers:
        "What happened?"

    It should not make provider-specific security decisions.
    """

    adapter_name: str
    provider_name: str

    @abstractmethod
    def normalize_event(
        self,
        raw_event: dict[str, Any],
        *,
        session_id: str | None = None,
        agent_id: str | None = None,
    ) -> CanonicalEvent:
        """
        Convert one provider-specific event into a CanonicalEvent.
        """
        raise NotImplementedError

    def normalize_events(
        self,
        raw_events: list[dict[str, Any]],
        *,
        session_id: str | None = None,
        agent_id: str | None = None,
    ) -> list[CanonicalEvent]:
        """
        Normalize a sequence while preserving event order.
        """
        return [
            self.normalize_event(
                raw_event,
                session_id=session_id,
                agent_id=agent_id,
            )
            for raw_event in raw_events
        ]

    def validate_connection(
        self,
        config: dict[str, Any],
    ) -> AdapterConnectionResult:
        """
        Validate adapter configuration.

        Local adapters generally do not require an external
        connection, so the default implementation is valid.
        """
        return AdapterConnectionResult(
            connected=True,
            adapter_name=self.adapter_name,
            provider_name=self.provider_name,
            message="Adapter configuration accepted.",
            metadata={},
        )

    def health_check(
        self,
        config: dict[str, Any],
    ) -> AdapterHealthResult:
        """
        Perform an adapter health check.
        """
        connection = self.validate_connection(config)

        return AdapterHealthResult(
            healthy=connection.connected,
            adapter_name=self.adapter_name,
            provider_name=self.provider_name,
            message=connection.message,
            metadata=connection.metadata,
        )