from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.domain.events.types import (
    EventStatus,
    EventType,
)
from app.infrastructure.postgres.models import Event
from app.repositories.interfaces import EventRepository
from app.schemas.audit import (
    AuditLogRequest,
    AuditLogResponse,
)


class AuditService:
    def __init__(
        self,
        repository: EventRepository,
    ):
        self.repository = repository

    async def record(
        self,
        request: AuditLogRequest,
        *,
        actor_user_id: str | None = None,
        actor_email: str | None = None,
        actor_role: str | None = None,
    ) -> AuditLogResponse:
        timestamp = datetime.now(timezone.utc)

        event_id = self._generate_event_id()

        metadata: dict[str, Any] = {
            **request.metadata,
            "audit": True,
            "actor_user_id": actor_user_id,
            "actor_email": actor_email,
            "actor_role": actor_role,
            "action": request.action,
            "resource_type": request.resource_type,
            "resource_id": request.resource_id,
        }

        event = Event(
            event_id=event_id,
            timestamp=timestamp,
            session_id=None,
            agent_id=None,
            provider="agenttrace",
            event_type=EventType.AUDIT_LOG.value,
            status=EventStatus.COMPLETED.value,
            tool=None,
            source="audit_service",
            severity=request.severity.upper(),
            details={
                "action": request.action,
                "resource_type": request.resource_type,
                "resource_id": request.resource_id,
                "description": request.description,
            },
            metadata=metadata,
            parent_event_id=None,
            related_event_id=None,
            trace_id=None,
            span_id=None,
        )

        persisted, _ = await self.repository.create_unique(event)

        return self._to_response(persisted)

    async def record_action(
        self,
        *,
        action: str,
        resource_type: str,
        resource_id: str | None,
        description: str,
        actor_user_id: str | None = None,
        actor_email: str | None = None,
        actor_role: str | None = None,
        severity: str = "LOW",
        metadata: dict[str, Any] | None = None,
    ) -> AuditLogResponse:
        request = AuditLogRequest(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            severity=severity,
            metadata=metadata or {},
        )

        return await self.record(
            request,
            actor_user_id=actor_user_id,
            actor_email=actor_email,
            actor_role=actor_role,
        )

    @staticmethod
    def _generate_event_id() -> str:
        import uuid

        return f"audit-{uuid.uuid4()}"

    @staticmethod
    def _to_response(
        event: Event,
    ) -> AuditLogResponse:
        details = event.details or {}
        metadata = event.metadata or {}

        return AuditLogResponse(
            audit_id=event.event_id,
            timestamp=event.timestamp,
            actor_user_id=metadata.get("actor_user_id"),
            actor_email=metadata.get("actor_email"),
            actor_role=metadata.get("actor_role"),
            action=str(details.get("action", "")),
            resource_type=str(details.get("resource_type", "")),
            resource_id=details.get("resource_id"),
            description=str(details.get("description", "")),
            severity=event.severity,
            metadata=metadata,
        )
