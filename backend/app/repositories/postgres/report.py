from __future__ import annotations

from sqlalchemy import select

from app.infrastructure.postgres.models import Report
from app.repositories.postgres.base import PostgresRepository


class PostgresReportRepository(
    PostgresRepository[Report]
):
    model = Report

    async def get_by_investigation(
        self,
        investigation_id: str,
    ) -> list[Report]:
        result = await self.session.execute(
            select(Report)
            .where(
                Report.investigation_id == investigation_id
            )
            .order_by(
                Report.created_at.desc()
            )
        )

        return list(result.scalars().all())

    async def get_latest_for_investigation(
        self,
        investigation_id: str,
    ) -> Report | None:
        result = await self.session.execute(
            select(Report)
            .where(
                Report.investigation_id == investigation_id
            )
            .order_by(
                Report.created_at.desc()
            )
            .limit(1)
        )

        return result.scalar_one_or_none()