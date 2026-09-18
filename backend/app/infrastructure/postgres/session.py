"""
PostgreSQL session utilities.

Repositories use these helpers to obtain SQLAlchemy sessions. The rest of
the application should interact with repositories rather than importing
SQLAlchemy session infrastructure directly.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.postgres.database import AsyncSessionFactory


@asynccontextmanager
async def session_scope() -> AsyncIterator[AsyncSession]:
    """
    Provide a transactional SQLAlchemy session.

    The transaction is committed when the context exits successfully and
    rolled back if an exception occurs.
    """

    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_repository_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency/helper for repository implementations.

    Unlike session_scope(), this function does not automatically commit.
    Repository methods can explicitly control transaction boundaries when
    multiple operations need to participate in one transaction.
    """

    async with AsyncSessionFactory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise