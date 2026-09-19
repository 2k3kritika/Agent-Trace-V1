from fastapi import APIRouter, Depends

from app.schemas.forensics import (
    ForensicAnalysisRequest,
    ForensicAnalysisResponse,
)
from app.services.dependency import (
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
    request: ForensicAnalysisRequest,
    service: InvestigationForensicService = Depends(get_investigation_forensic_service),
) -> ForensicAnalysisResponse:
    result = await service.analyze(
        investigation_id=investigation_id,
    )

    if not request.include_findings:
        result.findings = []

    if not request.include_timeline:
        result.timeline = []

    if not request.include_attack_graph:
        result.graph = None

    return ForensicAnalysisResponse.model_validate(result.model_dump(mode="python"))
