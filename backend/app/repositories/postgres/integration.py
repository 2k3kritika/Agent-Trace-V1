from __future__ import annotations

from app.core.exceptions import DuplicateResourceError, NotFoundError
from app.infrastructure.postgres.models import Integration
from app.repositories.interfaces import (
    RepositoryListResult,
)
from app.repositories.postgres.base import PostgresRepository
from sqlalchemy import Select, func, select
from sqlalchemy.exc import IntegrityError


class PostgresIntegrationRepository(PostgresRepository[Integration]):
    """PostgreSQL repository for agent integrations."""

    def __init__(self, db) -> None:
        super().__init__(
            db,
            Integration,
        )

    async def get_by_id(
        self,
        object_id: str,
    ) -> Integration:
        entity = await self.get_optional_by_id(object_id)

        if entity is None:
            raise NotFoundError(f"Integration '{object_id}' was not found.")

        return entity

    async def create(
        self,
        entity: Integration,
    ) -> Integration:
        self.db.add(entity)

        try:
            await self.db.flush()
            await self.db.refresh(entity)
            return entity

        except IntegrityError as exc:
            await self.db.rollback()

            raise DuplicateResourceError(
                "Integration could not be created because "
                "a database constraint was violated."
            ) from exc

    async def list(
        self,
        *,
        page: int = 1,
        page_size: int = 25,
        agent_id: str | None = None,
        status: str | None = None,
        provider: str | None = None,
        integration_type: str | None = None,
    ) -> RepositoryListResult[Integration]:
        filters = []

        if agent_id:
            filters.append(Integration.agent_id == agent_id)

        if status:
            filters.append(Integration.status == status)

        if provider:
            filters.append(Integration.provider == provider)

        if integration_type:
            filters.append(Integration.integration_type == integration_type)

        base_query: Select = select(Integration)

        if filters:
            base_query = base_query.where(*filters)

        count_query = select(func.count()).select_from(
            base_query.order_by(None).subquery()
        )

        total = int((await self.db.execute(count_query)).scalar_one())

        offset = (page - 1) * page_size

        query = (
            base_query.order_by(Integration.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )

        result = await self.db.execute(query)

        return RepositoryListResult(
            items=result.scalars().all(),
            total=total,
        )
