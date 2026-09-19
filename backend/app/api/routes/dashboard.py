from fastapi import APIRouter, Depends

from app.schemas.dashboard import DashboardOverviewResponse
from app.services.dashboard_service import DashboardService
from app.services.dependency import get_dashboard_service

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "/overview",
    response_model=DashboardOverviewResponse,
)
async def get_dashboard_overview(
    service: DashboardService = Depends(get_dashboard_service),
) -> DashboardOverviewResponse:
    return await service.get_overview()
