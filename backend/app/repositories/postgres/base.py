"""Shared PostgreSQL repository utilities."""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from sqlalchemy import Select, delete, func, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import RepositoryError
from app.core.exceptions import NotFoundError
from app.core.exceptions import DuplicateResourceError
ModelT = TypeVar("ModelT")


class PostgresRepository(Generic[ModelT]):
    """Base repository providing common PostgreSQL operations."""

    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _base_query(self) -> Select[Any]:
        """Return a base SELECT query for the repository model."""
        return select(self.model)

    async def get_by_id(self, record_id: str) -> ModelT:
        """Return a record by primary-key ID."""
        try:
            result = await self.session.get(self.model, record_id)
        except SQLAlchemyError as exc:
            raise RepositoryError(
                f"Failed to retrieve {self.model.__name__}: {exc}"
            ) from exc

        if result is None:
            raise NotFoundError(
                f"{self.model.__name__} with id '{record_id}' was not found."
            )

        return result

    async def get_optional_by_id(self, record_id: str) -> ModelT | None:
        """Return a record by ID or None when it does not exist."""
        try:
            return await self.session.get(self.model, record_id)
        except SQLAlchemyError as exc:
            raise RepositoryError(
                f"Failed to retrieve {self.model.__name__}: {exc}"
            ) from exc

    async def create(self, entity: ModelT) -> ModelT:
        """Persist a new entity."""
        try:
            self.session.add(entity)
            await self.session.flush()
            await self.session.refresh(entity)
            return entity
        except IntegrityError as exc:
            await self.session.rollback()
            raise DuplicateResourceError(
                f"Could not create {self.model.__name__}: integrity constraint failed."
            ) from exc
        except SQLAlchemyError as exc:
            await self.session.rollback()
            raise RepositoryError(
                f"Failed to create {self.model.__name__}: {exc}"
            ) from exc

    async def update(
        self,
        record_id: str,
        values: dict[str, Any],
    ) -> ModelT:
        """Update an entity and return the refreshed entity."""
        if not values:
            return await self.get_by_id(record_id)

        try:
            result = await self.session.execute(
                update(self.model)
                .where(self.model.id == record_id)
                .values(**values)
                .returning(self.model)
            )
            entity = result.scalar_one_or_none()

            if entity is None:
                raise NotFoundError(
                    f"{self.model.__name__} with id '{record_id}' was not found."
                )

            await self.session.flush()
            await self.session.refresh(entity)
            return entity

        except NotFoundError:
            raise
        except IntegrityError as exc:
            await self.session.rollback()
            raise DuplicateResourceError(
                f"Could not update {self.model.__name__}: integrity constraint failed."
            ) from exc
        except SQLAlchemyError as exc:
            await self.session.rollback()
            raise RepositoryError(
                f"Failed to update {self.model.__name__}: {exc}"
            ) from exc

    async def delete(self, record_id: str) -> None:
        """Delete an entity by ID."""
        try:
            result = await self.session.execute(
                delete(self.model)
                .where(self.model.id == record_id)
                .returning(self.model.id)
            )

            deleted_id = result.scalar_one_or_none()

            if deleted_id is None:
                raise NotFoundError(
                    f"{self.model.__name__} with id '{record_id}' was not found."
                )

            await self.session.flush()

        except NotFoundError:
            raise
        except SQLAlchemyError as exc:
            await self.session.rollback()
            raise RepositoryError(
                f"Failed to delete {self.model.__name__}: {exc}"
            ) from exc

    async def list_page(
        self,
        *,
        page: int,
        page_size: int,
        statement: Select[Any] | None = None,
    ) -> tuple[list[ModelT], int]:
        """Return one page of records and the total record count."""
        if page < 1:
            raise ValueError("page must be greater than or equal to 1.")

        if page_size < 1:
            raise ValueError("page_size must be greater than or equal to 1.")

        query = statement or self._base_query()

        try:
            count_query = select(func.count()).select_from(
                query.order_by(None).subquery()
            )

            total_result = await self.session.execute(count_query)
            total = int(total_result.scalar_one())

            offset = (page - 1) * page_size

            result = await self.session.execute(
                query.offset(offset).limit(page_size)
            )

            records = list(result.scalars().all())

            return records, total

        except SQLAlchemyError as exc:
            raise RepositoryError(
                f"Failed to list {self.model.__name__} records: {exc}"
            ) from exc