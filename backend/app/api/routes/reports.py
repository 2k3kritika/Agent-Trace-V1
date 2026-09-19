from fastapi import APIRouter, Depends, Query

from app.schemas.common import PaginationParams
from app.schemas.reports import (
    ReportCreateRequest,
    ReportListResponse,
    ReportResponse,
    ReportUpdateRequest,
)
from app.services.dependency import get_report_service
from app.services.report_service import ReportService

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


@router.post(
    "",
    response_model=ReportResponse,
)
async def create_report(
    request: ReportCreateRequest,
    service: ReportService = Depends(get_report_service),
) -> ReportResponse:
    return await service.create_report(request)


@router.get(
    "",
    response_model=ReportListResponse,
)
async def list_reports(
    pagination: PaginationParams = Depends(),
    investigation_id: str | None = Query(default=None),
    service: ReportService = Depends(get_report_service),
) -> ReportListResponse:
    return await service.list_reports(
        pagination=pagination,
        investigation_id=investigation_id,
    )


@router.get(
    "/{report_id}",
    response_model=ReportResponse,
)
async def get_report(
    report_id: str,
    service: ReportService = Depends(get_report_service),
) -> ReportResponse:
    return await service.get_report(report_id)


@router.patch(
    "/{report_id}",
    response_model=ReportResponse,
)
async def update_report(
    report_id: str,
    request: ReportUpdateRequest,
    service: ReportService = Depends(get_report_service),
) -> ReportResponse:
    return await service.update_report(
        report_id,
        request,
    )
