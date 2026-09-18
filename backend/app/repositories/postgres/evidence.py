from sqlalchemy import select

from app.infrastructure.postgres.models import Evidence
from app.repositories.postgres.base import PostgresRepository
from app.repositories.interfaces import RepositoryListResult


class PostgresEvidenceRepository(PostgresRepository[Evidence]):
    model = Evidence
    id_field = "evidence_id"

    async def get_by_investigation(
        self,
        investigation_id: str,
    ) -> list[Evidence]:
        result = await self.session.execute(
            select(Evidence)
            .where(Evidence.investigation_id == investigation_id)
            .order_by(Evidence.created_at.asc())
        )

        return list(result.scalars().all())

    async def list_page(
        self,
        *,
        page: int = 1,
        page_size: int = 25,
        investigation_id: str | None = None,
        evidence_type: str | None = None,
    ) -> RepositoryListResult[Evidence]:
        query = select(Evidence)

        if investigation_id:
            query = query.where(
                Evidence.investigation_id == investigation_id
            )

        if evidence_type:
            query = query.where(
                Evidence.evidence_type == evidence_type
            )

        return await super().list_page(
            page=page,
            page_size=page_size,
            query=query,
        )