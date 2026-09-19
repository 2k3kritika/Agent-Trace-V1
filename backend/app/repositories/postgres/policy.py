"""PostgreSQL repository for security policies."""

from __future__ import annotations

from app.infrastructure.postgres.models import Policy
from app.repositories.interfaces import (
    PolicyRepository,
)
from app.repositories.postgres.base import PostgresRepository
from sqlalchemy import select


class PostgresPolicyRepository(
    PostgresRepository[Policy],
    PolicyRepository,
):
    """PostgreSQL implementation of PolicyRepository."""

    model = Policy

    async def get_by_policy_id(
        self,
        policy_id: str,
    ) -> Policy:
        """Retrieve a policy by ID."""
        return await self.get_by_id(policy_id)

    async def list_policies(
        self,
        *,
        page: int,
        page_size: int,
        status: str | None = None,
        search: str | None = None,
    ) -> tuple[list[Policy], int]:
        """List policies with optional filtering."""
        statement = select(Policy)

        if status:
            statement = statement.where(Policy.status == status)

        if search:
            pattern = f"%{search.strip()}%"
            statement = statement.where(
                Policy.name.ilike(pattern) | Policy.description.ilike(pattern)
            )

        statement = statement.order_by(
            Policy.priority.asc(),
            Policy.created_at.asc(),
        )

        return await self.list_page(
            page=page,
            page_size=page_size,
            statement=statement,
        )

    async def list_active_policies(
        self,
    ) -> list[Policy]:
        """Return active policies ordered by priority."""
        result = await self.session.execute(
            select(Policy)
            .where(Policy.status == "active")
            .order_by(Policy.priority.asc())
        )

        return list(result.scalars().all())
