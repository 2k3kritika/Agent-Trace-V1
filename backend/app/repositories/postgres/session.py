"""PostgreSQL repository for agent sessions."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import select

from app.infrastructure.postgres.models import Session
from app.core.exceptions import DuplicateResourceError
from app.repositories.interfaces import (
    SessionRepository,
)
from app.core.exceptions import NotFoundError
from app.repositories.postgres.base import PostgresRepository


class PostgresSessionRepository(
    PostgresRepository[Session],
    SessionRepository,
):
    """PostgreSQL implementation of SessionRepository."""

    model = Session

    async def get_by_session_id(self, session_id: str) -> Session:
        """Retrieve a session using its public session ID."""
        result = await self.session.execute(
            select(Session).where(Session.session_id == session_id)
        )

        session = result.scalar_one_or_none()

        if session is None:
            raise NotFoundError(
                f"Session with session_id '{session_id}' was not found."
            )

        return session

    async def get_optional_by_session_id(
        self,
        session_id: str,
    ) -> Session | None:
        """Retrieve a session or return None."""
        result = await self.session.execute(
            select(Session).where(Session.session_id == session_id)
        )

        return result.scalar_one_or_none()

    async def create_unique(self, entity: Session) -> Session:
        """Create a session while preventing duplicate session IDs."""
        existing = await self.get_optional_by_session_id(entity.session_id)

        if existing is not None:
            raise DuplicateResourceError(
                f"Session with session_id '{entity.session_id}' already exists."
            )

        return await self.create(entity)

    async def list_sessions(
        self,
        *,
        page: int,
        page_size: int,
        agent_id: str | None = None,
        status: str | None = None,
        risk_level: str | None = None,
        from_timestamp: datetime | None = None,
        to_timestamp: datetime | None = None,
        search: str | None = None,
    ) -> tuple[list[Session], int]:
        """List sessions using dashboard/investigation filters."""
        statement = select(Session)

        if agent_id:
            statement = statement.where(Session.agent_id == agent_id)

        if status:
            statement = statement.where(Session.status == status)

        if risk_level:
            statement = statement.where(Session.risk_level == risk_level)

        if from_timestamp:
            statement = statement.where(Session.started_at >= from_timestamp)

        if to_timestamp:
            statement = statement.where(Session.started_at <= to_timestamp)

        if search:
            pattern = f"%{search.strip()}%"
            statement = statement.where(
                Session.session_id.ilike(pattern)
                | Session.provider.ilike(pattern)
                | Session.scenario.ilike(pattern)
            )

        statement = statement.order_by(
            Session.started_at.desc(),
        )

        return await self.list_page(
            page=page,
            page_size=page_size,
            statement=statement,
        )

    async def update_metrics(
        self,
        session_id: str,
        *,
        event_count: int | None = None,
        alert_count: int | None = None,
        risk_score: int | None = None,
        risk_level: str | None = None,
        duration: float | None = None,
        ended_at: datetime | None = None,
        status: str | None = None,
    ) -> Session:
        """Update calculated session telemetry metrics."""
        session = await self.get_by_session_id(session_id)

        values: dict[str, Any] = {}

        if event_count is not None:
            values["event_count"] = event_count

        if alert_count is not None:
            values["alert_count"] = alert_count

        if risk_score is not None:
            values["risk_score"] = risk_score

        if risk_level is not None:
            values["risk_level"] = risk_level

        if duration is not None:
            values["duration"] = duration

        if ended_at is not None:
            values["ended_at"] = ended_at

        if status is not None:
            values["status"] = status

        return await self.update(session.id, values)