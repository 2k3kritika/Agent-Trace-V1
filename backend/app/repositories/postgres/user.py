from __future__ import annotations

from app.infrastructure.postgres.models import User
from app.repositories.postgres.base import PostgresRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class PostgresUserRepository(PostgresRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, User)

    async def get_by_email(
        self,
        email: str,
    ) -> User | None:
        result = await self.db.execute(
            select(User).where(User.email == email.lower().strip())
        )

        return result.scalar_one_or_none()

    async def get_active_by_id(
        self,
        user_id: str,
    ) -> User | None:
        result = await self.db.execute(
            select(User).where(
                User.id == user_id,
                User.is_active.is_(True),
            )
        )

        return result.scalar_one_or_none()

    async def email_exists(
        self,
        email: str,
    ) -> bool:
        result = await self.db.execute(
            select(User.id).where(User.email == email.lower().strip())
        )

        return result.scalar_one_or_none() is not None
