from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.common import MessageResponse, PaginationParams
from app.schemas.evidence import (
    EvidenceCreateRequest,
    EvidenceListResponse,
    EvidenceResponse,
    EvidenceUpdateRequest,
)
from app.services.dependency import (
    get_db_session,
    get_evidence_service,
)
from app.services.evidence_service import EvidenceService

router = APIRouter(
    prefix="/evidence",
    tags=["Evidence"],
)


@router.post(
    "",
    response_model=EvidenceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_evidence(
    request: EvidenceCreateRequest,
    db: AsyncSession = Depends(get_db_session),
) -> EvidenceResponse:
    service = get_evidence_service(db)

    return await service.create_evidence(request)


@router.get(
    "",
    response_model=EvidenceListResponse,
)
async def list_evidence(
    pagination: PaginationParams = Depends(),
    investigation_id: str | None = Query(default=None),
    evidence_type: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db_session),
) -> EvidenceListResponse:
    service = get_evidence_service(db)

    items, total = await service.list_evidence(
        page=pagination.page,
        page_size=pagination.page_size,
        investigation_id=investigation_id,
        evidence_type=evidence_type,
    )

    return EvidenceListResponse(
        items=items,
        page=pagination.page,
        page_size=pagination.page_size,
        total=total,
        has_next=(
            pagination.page * pagination.page_size < total
        ),
    )


@router.get(
    "/investigation/{investigation_id}",
    response_model=list[EvidenceResponse],
)
async def list_investigation_evidence(
    investigation_id: str,
    db: AsyncSession = Depends(get_db_session),
) -> list[EvidenceResponse]:
    service = get_evidence_service(db)

    return await service.list_investigation_evidence(
        investigation_id
    )


@router.get(
    "/{evidence_id}",
    response_model=EvidenceResponse,
)
async def get_evidence(
    evidence_id: str,
    db: AsyncSession = Depends(get_db_session),
) -> EvidenceResponse:
    service = get_evidence_service(db)

    return await service.get_evidence(evidence_id)


@router.patch(
    "/{evidence_id}",
    response_model=EvidenceResponse,
)
async def update_evidence(
    evidence_id: str,
    request: EvidenceUpdateRequest,
    db: AsyncSession = Depends(get_db_session),
) -> EvidenceResponse:
    service = get_evidence_service(db)

    return await service.update_evidence(
        evidence_id,
        request,
    )


@router.delete(
    "/{evidence_id}",
    response_model=MessageResponse,
)
async def delete_evidence(
    evidence_id: str,
    db: AsyncSession = Depends(get_db_session),
) -> MessageResponse:
    service = get_evidence_service(db)

    await service.delete_evidence(evidence_id)

    return MessageResponse(
        message="Evidence deleted successfully."
    )