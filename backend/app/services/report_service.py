from __future__ import annotations

from datetime import datetime, timezone

from app.core.exceptions import ReportNotFoundError
from app.infrastructure.postgres.models import Report
from app.repositories.interfaces import ReportRepository
from app.schemas.common import PaginationParams
from app.schemas.reports import (
    ReportCreateRequest,
    ReportListResponse,
    ReportResponse,
    ReportUpdateRequest,
)


class ReportService:
    def __init__(
        self,
        repository: ReportRepository,
    ):
        self.repository = repository

    @staticmethod
    def _to_response(report: Report) -> ReportResponse:
        return ReportResponse.model_validate(
            {
                "id": report.id,
                "investigation_id": report.investigation_id,
                "report_type": report.report_type,
                "status": report.status,
                "title": report.title,
                "content": report.content,
                "storage_uri": report.storage_uri,
                "metadata": report.metadata or {},
                "created_at": report.created_at,
                "updated_at": report.updated_at,
            }
        )

    async def create_report(
        self,
        request: ReportCreateRequest,
    ) -> ReportResponse:
        title = (
            request.title
            or f"{request.report_type.title()} Investigation Report"
        )

        report = Report(
            investigation_id=request.investigation_id,
            report_type=request.report_type,
            status="GENERATING",
            title=title,
            content=None,
            storage_uri=None,
            metadata={},
        )

        created = await self.repository.create(report)

        return self._to_response(created)

    async def get_report(
        self,
        report_id: str,
    ) -> ReportResponse:
        report = await self.repository.get_by_id(report_id)

        if report is None:
            raise ReportNotFoundError(
                message=f"Report '{report_id}' was not found.",
    )

        return self._to_response(report)

    async def list_reports(
        self,
        pagination: PaginationParams,
        investigation_id: str | None = None,
    ) -> ReportListResponse:
        result = await self.repository.list_page(
            page=pagination.page,
            page_size=pagination.page_size,
            investigation_id=investigation_id,
        )

        items = [
            self._to_response(report)
            for report in result.items
        ]

        return ReportListResponse(
            items=items,
            page=pagination.page,
            page_size=pagination.page_size,
            total=result.total,
            has_next=(
                pagination.page * pagination.page_size
                < result.total
            ),
        )

async def update_report(
    self,
    report_id: str,
    request: ReportUpdateRequest,
) -> ReportResponse:
    report = await self.repository.get_by_id(report_id)

    if report is None:
        raise ReportNotFoundError(
            message=f"Report '{report_id}' was not found.",
        )

    updates = request.model_dump(
        exclude_unset=True,
        exclude_none=True,
    )

    for field_name, value in updates.items():
        setattr(report, field_name, value)

    report.updated_at = datetime.now(timezone.utc)

    updated = await self.repository.update(
        report_id,
        report,
    )

    return self._to_response(updated)