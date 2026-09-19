"""PostgreSQL repository for alerts."""

from __future__ import annotations

from datetime import datetime

from app.core.exceptions import NotFoundError
from app.infrastructure.postgres.models import Alert
from app.repositories.interfaces import AlertRepository
from app.repositories.postgres.base import PostgresRepository
from sqlalchemy import select


class PostgresAlertRepository(
    PostgresRepository[Alert],
    AlertRepository,
):
    """PostgreSQL implementation of AlertRepository."""

    model = Alert

    async def get_by_alert_id(
        self,
        alert_id: str,
    ) -> Alert:
        """Retrieve an alert using its public alert ID."""
        result = await self.session.execute(
            select(Alert).where(Alert.alert_id == alert_id)
        )

        alert = result.scalar_one_or_none()

        if alert is None:
            raise NotFoundError(f"Alert '{alert_id}' was not found.")

        return alert

    async def list_alerts(
        self,
        *,
        page: int,
        page_size: int,
        agent_id: str | None = None,
        session_id: str | None = None,
        investigation_id: str | None = None,
        severity: str | None = None,
        status: str | None = None,
        from_timestamp: datetime | None = None,
        to_timestamp: datetime | None = None,
        search: str | None = None,
    ) -> tuple[list[Alert], int]:
        """List alerts with filtering and pagination."""
        statement = select(Alert)

        if agent_id:
            statement = statement.where(Alert.agent_id == agent_id)

        if session_id:
            statement = statement.where(Alert.session_id == session_id)

        if investigation_id:
            statement = statement.where(Alert.investigation_id == investigation_id)

        if severity:
            statement = statement.where(Alert.severity == severity)

        if status:
            statement = statement.where(Alert.status == status)

        if from_timestamp:
            statement = statement.where(Alert.created_at >= from_timestamp)

        if to_timestamp:
            statement = statement.where(Alert.created_at <= to_timestamp)

        if search:
            pattern = f"%{search.strip()}%"
            statement = statement.where(
                Alert.title.ilike(pattern)
                | Alert.description.ilike(pattern)
                | Alert.detector_id.ilike(pattern)
            )

        statement = statement.order_by(
            Alert.created_at.desc(),
        )

        return await self.list_page(
            page=page,
            page_size=page_size,
            statement=statement,
        )

    async def list_investigation_alerts(
        self,
        investigation_id: str,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[Alert], int]:
        """Return alerts associated with one investigation."""
        statement = (
            select(Alert)
            .where(Alert.investigation_id == investigation_id)
            .order_by(Alert.created_at.desc())
        )

        return await self.list_page(
            page=page,
            page_size=page_size,
            statement=statement,
        )
