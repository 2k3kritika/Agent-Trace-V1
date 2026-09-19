from __future__ import annotations

from typing import Any

from app.domain.detection.models import DetectionFinding
from app.domain.events.types import EventSeverity
from app.infrastructure.postgres.models import Alert
from app.repositories.interfaces import AlertRepository


class AlertService:
    """
    Application service responsible for creating and retrieving alerts.

    Detection produces findings.
    AlertService converts findings into persistent security alerts.
    """

    def __init__(
        self,
        repository: AlertRepository,
    ) -> None:
        self.repository = repository

    async def create_alert(
        self,
        *,
        title: str,
        description: str,
        severity: EventSeverity,
        agent_id: str | None = None,
        session_id: str | None = None,
        investigation_id: str | None = None,
        detector_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Alert:
        alert = Alert(
            title=title,
            description=description,
            severity=severity.value,
            status="OPEN",
            agent_id=agent_id,
            session_id=session_id,
            investigation_id=investigation_id,
            detector_id=detector_id,
            metadata=metadata or {},
        )

        return await self.repository.create(alert)

    async def create_from_finding(
        self,
        finding: DetectionFinding,
        *,
        agent_id: str | None = None,
        session_id: str | None = None,
        investigation_id: str | None = None,
    ) -> Alert:
        return await self.create_alert(
            title=finding.title,
            description=finding.description,
            severity=finding.severity,
            agent_id=agent_id,
            session_id=session_id,
            investigation_id=investigation_id,
            detector_id=finding.detector_id,
            metadata={
                "event_id": finding.event_id,
                "confidence": finding.confidence,
                "evidence": finding.evidence,
                **finding.metadata,
            },
        )

    async def create_from_findings(
        self,
        findings: list[DetectionFinding],
        *,
        agent_id: str | None = None,
        session_id: str | None = None,
        investigation_id: str | None = None,
    ) -> list[Alert]:
        alerts: list[Alert] = []

        for finding in findings:
            alert = await self.create_from_finding(
                finding,
                agent_id=agent_id,
                session_id=session_id,
                investigation_id=investigation_id,
            )

            alerts.append(alert)

        return alerts

    async def get_alert(
        self,
        alert_id: str,
    ) -> Alert:
        return await self.repository.get_by_id(alert_id)

    async def list_alerts(
        self,
        *,
        page: int = 1,
        page_size: int = 25,
        severity: EventSeverity | None = None,
        status: str | None = None,
    ):
        filters: dict[str, Any] = {}

        if severity is not None:
            filters["severity"] = severity.value

        if status is not None:
            filters["status"] = status

        return await self.repository.list_page(
            page=page,
            page_size=page_size,
            filters=filters,
        )
