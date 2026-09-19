"""
PostgreSQL session utilities.

Repositories use these helpers to obtain SQLAlchemy sessions. The rest of
the application should interact with repositories rather than importing
SQLAlchemy session infrastructure directly.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager

from app.infrastructure.postgres.database import AsyncSessionFactory
from app.repositories.factory import is_dynamodb_backend
from sqlalchemy.ext.asyncio import AsyncSession


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


async def get_repository_session() -> AsyncGenerator[AsyncSession | None, None]:
    """
    Provide a repository session for PostgreSQL.

    DynamoDB-backed environments do not require a PostgreSQL session,
    so they receive None instead.
    """
    if is_dynamodb_backend():
        yield None
        return

    async with AsyncSessionFactory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise