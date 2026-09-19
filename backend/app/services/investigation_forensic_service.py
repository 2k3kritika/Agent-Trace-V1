from __future__ import annotations

from app.core.exceptions import InvestigationNotFoundError
from app.domain.events.models import CanonicalEvent
from app.domain.forensics.models import ForensicAnalysisResult
from app.schemas.investigations import InvestigationUpdateRequest
from app.services.event_service import EventService
from app.services.evidence_service import EvidenceService
from app.services.forensic_service import ForensicService
from app.services.investigation_service import InvestigationService


class InvestigationForensicService:
    def __init__(
        self,
        investigation_service: InvestigationService,
        event_service: EventService,
        evidence_service: EvidenceService,
        forensic_service: ForensicService,
    ) -> None:
        self.investigation_service = investigation_service
        self.event_service = event_service
        self.evidence_service = evidence_service
        self.forensic_service = forensic_service

    async def analyze(
        self,
        investigation_id: str,
    ) -> ForensicAnalysisResult:
        investigation = await self.investigation_service.get_investigation(
            investigation_id
        )

        if investigation is None:
            raise InvestigationNotFoundError(
                f"Investigation '{investigation_id}' was not found."
            )

        event_responses = await self.event_service.list_session_events(
            investigation.session_id
        )

        events = [
            CanonicalEvent.model_validate(
                event.model_dump(mode="python")
            )
            for event in event_responses
        ]

        result = self.forensic_service.analyze(
            investigation_id=investigation_id,
            events=events,
        )

        await self._persist_result(
            investigation_id,
            result,
        )

        return result

    async def _persist_result(
        self,
        investigation_id: str,
        result: ForensicAnalysisResult,
    ) -> None:
        existing = await self.investigation_service.get_investigation(
            investigation_id
        )

        if existing is None:
            raise InvestigationNotFoundError(
                f"Investigation '{investigation_id}' was not found."
            )

        existing_summary = dict(existing.summary or {})

        existing_summary.update(
            {
                "forensic_findings": len(result.findings),
                "timeline": [
                    item.model_dump(mode="json")
                    for item in result.timeline
                ],
                "event_count": result.event_count,
                "security_event_count": result.security_event_count,
                "suspicious_event_count": result.suspicious_event_count,
                "sensitive_action_count": result.sensitive_action_count,
                "blocked_action_count": result.blocked_action_count,
                "forensic_summary": result.summary,
            }
        )

        update_request = InvestigationUpdateRequest(
            summary=existing_summary,
            graph=result.graph.model_dump(mode="json"),
        )

        await self.investigation_service.update_investigation(
            investigation_id,
            update_request,
        )