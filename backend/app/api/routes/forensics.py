from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.forensics import ForensicAnalysisResponse, finding_to_response
from app.services.dependency import (
    get_db_session,
    get_investigation_forensic_service,
)
from app.services.investigation_forensic_service import (
    InvestigationForensicService,
)

router = APIRouter(
    prefix="/forensics",
    tags=["Forensics"],
)


@router.post(
    "/investigations/{investigation_id}/analyze",
    response_model=ForensicAnalysisResponse,
)
async def analyze_investigation(
    investigation_id: str,
    db: AsyncSession = Depends(get_db_session),
) -> ForensicAnalysisResponse:
    service = get_investigation_forensic_service(db)

    result = await service.analyze(
        investigation_id
    )

    return ForensicAnalysisResponse(
        investigation_id=result.investigation_id,
        findings=[
            finding_to_response(finding)
            for finding in result.findings
        ],
        graph=result.graph,
        evidence_count=result.evidence_count,
        security_event_count=result.security_event_count,
        timeline_start=result.timeline_start,
        timeline_end=result.timeline_end,
        summary=result.summary,
    )