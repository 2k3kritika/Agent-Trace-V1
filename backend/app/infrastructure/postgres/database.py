"""
PostgreSQL database infrastructure for local development.

The application layer should never import this module directly. Services
will eventually depend on repository interfaces, while repositories use
this infrastructure layer.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings


settings = get_settings()


def create_engine() -> AsyncEngine:
    """
    Create the application's asynchronous SQLAlchemy engine.
    """

    return create_async_engine(
        settings.database_url,
        echo=settings.debug,
        pool_pre_ping=True,
        future=True,
    )


engine = create_engine()


AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides one database session per request.
    """

    async with AsyncSessionFactory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def dispose_engine() -> None:
    """
    Dispose the SQLAlchemy engine during application shutdown.
    """

    await engine.dispose()