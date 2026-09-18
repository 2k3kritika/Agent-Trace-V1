from datetime import datetime, timezone

from app.domain.events.models import CanonicalEvent
from app.domain.events.types import (
    EventSeverity,
    EventStatus,
    EventType,
)
from app.domain.forensics.models import ForensicAnalysisResult
from app.services.evidence_service import EvidenceService
from app.services.forensic_service import ForensicService
from app.services.investigation_service import InvestigationService
from app.services.event_service import EventService


class InvestigationForensicService:
    """
    Orchestrates persistence-backed forensic analysis.

    Flow:

        Investigation
            -> Events
            -> Evidence count
            -> ForensicService
            -> Investigation summary/graph persistence
    """

    def __init__(
        self,
        investigation_service: InvestigationService,
        event_service: EventService,
        evidence_service: EvidenceService,
        forensic_service: ForensicService,
    ):
        self.investigation_service = investigation_service
        self.event_service = event_service
        self.evidence_service = evidence_service
        self.forensic_service = forensic_service

    async def analyze(
        self,
        investigation_id: str,
    ) -> ForensicAnalysisResult:
        investigation = (
            await self.investigation_service.get_investigation(
                investigation_id
            )
        )

        events = await self._load_events(
            investigation_id=investigation_id,
            session_id=investigation.session_id,
        )

        evidence = (
            await self.evidence_service.list_investigation_evidence(
                investigation_id
            )
        )

        result = self.forensic_service.analyze(
            investigation_id=investigation_id,
            events=events,
            evidence_count=len(evidence),
        )

        await self._persist_result(
            investigation_id=investigation_id,
            result=result,
        )

        return result

    async def _load_events(
        self,
        *,
        investigation_id: str,
        session_id: str | None,
    ) -> list[CanonicalEvent]:
        if not session_id:
            return []

        event_responses = (
            await self.event_service.list_session_events(
                session_id
            )
        )

        events: list[CanonicalEvent] = []

        for event in event_responses:
            events.append(
                CanonicalEvent.model_validate(
                    event.model_dump()
                )
            )

        return events

    async def _persist_result(
        self,
        *,
        investigation_id: str,
        result: ForensicAnalysisResult,
    ) -> None:
        investigation = (
            await self.investigation_service.get_investigation(
                investigation_id
            )
        )

        existing_summary = (
            investigation.summary
            if isinstance(investigation.summary, dict)
            else {}
        )

        existing_summary.update(
            {
                "forensic": result.summary,
                "timeline_start": (
                    result.timeline_start.isoformat()
                    if result.timeline_start
                    else None
                ),
                "timeline_end": (
                    result.timeline_end.isoformat()
                    if result.timeline_end
                    else None
                ),
                "finding_count": len(result.findings),
            }
        )

        await self.investigation_service.update_investigation(
            investigation_id,
            {
                "summary": existing_summary,
                "graph": result.graph.model_dump(mode="json"),
            },
        )