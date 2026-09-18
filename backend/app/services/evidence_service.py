from app.infrastructure.postgres.models import Evidence
from app.repositories.interfaces import EvidenceRepository
from app.schemas.evidence import (
    EvidenceCreateRequest,
    EvidenceResponse,
    EvidenceUpdateRequest,
)


class EvidenceService:
    def __init__(self, repository: EvidenceRepository):
        self.repository = repository

    async def create_evidence(
        self,
        request: EvidenceCreateRequest,
    ) -> EvidenceResponse:
        evidence = Evidence(
            investigation_id=request.investigation_id,
            event_id=request.event_id,
            evidence_type=request.evidence_type,
            title=request.title,
            description=request.description,
            storage_uri=request.storage_uri,
            sha256=request.sha256,
            content=request.content,
            metadata=request.metadata,
        )

        created = await self.repository.create(evidence)

        return self._to_response(created)

    async def get_evidence(
        self,
        evidence_id: str,
    ) -> EvidenceResponse:
        evidence = await self.repository.get_by_id(evidence_id)
        return self._to_response(evidence)

    async def list_evidence(
        self,
        *,
        page: int = 1,
        page_size: int = 25,
        investigation_id: str | None = None,
        evidence_type: str | None = None,
    ) -> tuple[list[EvidenceResponse], int]:
        result = await self.repository.list_page(
            page=page,
            page_size=page_size,
            investigation_id=investigation_id,
            evidence_type=evidence_type,
        )

        return (
            [self._to_response(item) for item in result.items],
            result.total,
        )

    async def list_investigation_evidence(
        self,
        investigation_id: str,
    ) -> list[EvidenceResponse]:
        items = await self.repository.get_by_investigation(
            investigation_id
        )

        return [self._to_response(item) for item in items]

    async def update_evidence(
        self,
        evidence_id: str,
        request: EvidenceUpdateRequest,
    ) -> EvidenceResponse:
        evidence = await self.repository.get_by_id(evidence_id)

        updates = request.model_dump(exclude_unset=True)

        for field, value in updates.items():
            setattr(evidence, field, value)

        updated = await self.repository.update(evidence)

        return self._to_response(updated)

    async def delete_evidence(
        self,
        evidence_id: str,
    ) -> None:
        await self.repository.delete(evidence_id)

    @staticmethod
    def _to_response(evidence: Evidence) -> EvidenceResponse:
        return EvidenceResponse(
            evidence_id=evidence.evidence_id,
            investigation_id=evidence.investigation_id,
            event_id=evidence.event_id,
            evidence_type=evidence.evidence_type,
            title=evidence.title,
            description=evidence.description,
            storage_uri=evidence.storage_uri,
            sha256=evidence.sha256,
            content=evidence.content,
            metadata=evidence.metadata or {},
            created_at=evidence.created_at,
            updated_at=evidence.updated_at,
        )