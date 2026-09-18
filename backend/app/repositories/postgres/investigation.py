"""PostgreSQL repository for investigations."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select

from app.infrastructure.postgres.models import Investigation
from app.core.exceptions import DuplicateResourceError
from app.repositories.interfaces import (
    InvestigationRepository,
)
from app.core.exceptions import NotFoundError
from app.repositories.postgres.base import PostgresRepository


class PostgresInvestigationRepository(
    PostgresRepository[Investigation],
    InvestigationRepository,
):
    """PostgreSQL implementation of InvestigationRepository."""

    model = Investigation

    async def get_by_investigation_id(
        self,
        investigation_id: str,
    ) -> Investigation:
        """Retrieve an investigation by its public ID."""
        result = await self.session.execute(
            select(Investigation).where(
                Investigation.id == investigation_id
            )
        )

        investigation = result.scalar_one_or_none()

        if investigation is None:
            raise NotFoundError(
                f"Investigation '{investigation_id}' was not found."
            )

        return investigation

    async def get_by_session_id(
        self,
        session_id: str,
    ) -> Investigation | None:
        """Retrieve the investigation associated with a session."""
        result = await self.session.execute(
            select(Investigation)
            .where(Investigation.session_id == session_id)
            .order_by(Investigation.created_at.desc())
            .limit(1)
        )

        return result.scalar_one_or_none()

    async def create_unique(
        self,
        entity: Investigation,
    ) -> Investigation:
        """Create an investigation."""
        existing = await self.get_by_session_id(entity.session_id)

        if existing is not None:
            raise DuplicateResourceError(
                "An investigation already exists for this session."
            )

        return await self.create(entity)

    async def list_investigations(
        self,
        *,
        page: int,
        page_size: int,
        agent_id: str | None = None,
        severity: str | None = None,
        status: str | None = None,
        from_timestamp: datetime | None = None,
        to_timestamp: datetime | None = None,
        search: str | None = None,
    ) -> tuple[list[Investigation], int]:
        """List investigations using dashboard filters."""
        statement = select(Investigation)

        if agent_id:
            statement = statement.where(
                Investigation.agent_id == agent_id
            )

        if severity:
            statement = statement.where(
                Investigation.risk_level == severity
            )

        if status:
            statement = statement.where(
                Investigation.status == status
            )

        if from_timestamp:
            statement = statement.where(
                Investigation.created_at >= from_timestamp
            )

        if to_timestamp:
            statement = statement.where(
                Investigation.created_at <= to_timestamp
            )

        if search:
            pattern = f"%{search.strip()}%"
            statement = statement.where(
                Investigation.scenario.ilike(pattern)
                | Investigation.attack_vector.ilike(pattern)
                | Investigation.verdict_type.ilike(pattern)
            )

        statement = statement.order_by(
            Investigation.created_at.desc(),
        )

        return await self.list_page(
            page=page,
            page_size=page_size,
            statement=statement,
        )