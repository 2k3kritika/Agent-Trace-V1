from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.infrastructure.postgres.models import Session
from app.repositories.interfaces import (
    RepositoryListResult,
    SessionRepository,
)


class SessionService:
    """Application service for agent execution sessions."""

    def __init__(
        self,
        repository: SessionRepository,
    ) -> None:
        self.repository = repository

    async def get_session(
        self,
        session_id: str,
    ) -> Session:
        """Retrieve a session by its public session ID."""
        return await self.repository.get_by_session_id(session_id)

    async def get_session_optional(
        self,
        session_id: str,
    ) -> Session | None:
        """Retrieve a session or return None."""
        return await self.repository.get_optional_by_session_id(
            session_id
        )

    async def create_session(
        self,
        *,
        session_id: str,
        agent_id: str,
        provider: str | None = None,
        scenario: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[Session, bool]:
        """Create a session unless the session ID already exists."""

        existing = await self.repository.get_optional_by_session_id(
            session_id
        )

        if existing is not None:
            return existing, False

        session = Session(
            session_id=session_id,
            agent_id=agent_id,
            provider=provider or "unknown",
            status="ACTIVE",
            started_at=datetime.now(timezone.utc),
            ended_at=None,
            duration=None,
            event_count=0,
            alert_count=0,
            risk_score=0,
            risk_level="LOW",
            scenario=scenario,
            metadata_json=metadata or {},
        )

        return await self.repository.create_unique(session)

    async def update_metrics(
        self,
        session_id: str,
        *,
        event_count: int | None = None,
        alert_count: int | None = None,
        risk_score: int | None = None,
        risk_level: str | None = None,
    ) -> Session:
        """Update calculated telemetry and risk metrics."""

        normalized_score = None

        if risk_score is not None:
            normalized_score = max(
                0,
                min(100, risk_score),
            )

        return await self.repository.update_metrics(
            session_id=session_id,
            event_count=event_count,
            alert_count=alert_count,
            risk_score=normalized_score,
            risk_level=risk_level,
        )

    async def close_session(
        self,
        session_id: str,
    ) -> Session:
        """Mark a running session as completed."""

        session = await self.repository.get_by_session_id(session_id)

        ended_at = datetime.now(timezone.utc)

        duration: float | None = None

        if session.started_at is not None:
            duration = max(
                0.0,
                (ended_at - session.started_at).total_seconds(),
            )

        session.status = "COMPLETED"
        session.ended_at = ended_at
        session.duration = duration

        return await self.repository.update(session)

    async def list_sessions(
        self,
        *,
        page: int = 1,
        page_size: int = 25,
        agent_id: str | None = None,
        status: str | None = None,
        risk_level: str | None = None,
        search: str | None = None,
    ) -> RepositoryListResult[Session]:
        """List sessions using dashboard/investigation filters."""

        return await self.repository.list(
            page=page,
            page_size=page_size,
            agent_id=agent_id,
            status=status,
            risk_level=risk_level,
            search=search,
        )