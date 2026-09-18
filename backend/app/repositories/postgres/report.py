from __future__ import annotations

from sqlalchemy import Select, func, select
from sqlalchemy.exc import IntegrityError

from app.infrastructure.postgres.models import Report
from app.core.exceptions import DuplicateResourceError
from app.repositories.interfaces import (
    RepositoryListResult,
)
from app.core.exceptions import NotFoundError
from app.repositories.postgres.base import PostgresRepository


class PostgresReportRepository(PostgresRepository[Report]):
    """PostgreSQL repository for generated investigation reports."""

    def __init__(self, db):
        super().__init__(db, Report)

    async def create(self, entity: Report) -> Report:
        self.db.add(entity)

        try:
            await self.db.flush()
            await self.db.refresh(entity)
            return entity
        except IntegrityError as exc:
            await self.db.rollback()
            raise DuplicateResourceError(
                "Report could not be created because a database "
                "constraint was violated."
            ) from exc

    async def get_by_id(self, object_id: str) -> Report:
        entity = await self.get_optional_by_id(object_id)

        if entity is None:
            raise NotFoundError(
                f"Report '{object_id}' was not found."
            )

        return entity

    async def list(
        self,
        *,
        page: int = 1,
        page_size: int = 25,
        investigation_id: str | None = None,
        report_type: str | None = None,
        status: str | None = None,
    ) -> RepositoryListResult[Report]:
        filters = []

        if investigation_id:
            filters.append(
                Report.investigation_id == investigation_id
            )

        if report_type:
            filters.append(Report.report_type == report_type)

        if status:
            filters.append(Report.status == status)

        base_query: Select = select(Report)

        if filters:
            base_query = base_query.where(*filters)

        count_query = select(func.count()).select_from(
            base_query.order_by(None).subquery()
        )

        total = int((await self.db.execute(count_query)).scalar_one())

        offset = (page - 1) * page_size

        query = (
            base_query.order_by(Report.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )

        result = await self.db.execute(query)

        return RepositoryListResult(
            items=result.scalars().all(),
            total=total,
        )