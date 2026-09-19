from __future__ import annotations

from app.domain.correlation.models import (
    CorrelationCandidate,
    CorrelationResult,
)
from app.domain.events.models import CanonicalEvent
from app.domain.events.types import (
    EventRelationshipType,
    EventType,
)
from app.schemas.correlation import (
    CorrelationRequest,
    CorrelationResponse,
)


class CorrelationService:
    def correlate(
        self,
        session_id: str,
        events: list[CanonicalEvent],
        request: CorrelationRequest | None = None,
    ) -> CorrelationResponse:
        request = request or CorrelationRequest()

        ordered_events = sorted(
            events,
            key=lambda event: event.timestamp,
        )

        relationships: list[CorrelationCandidate] = []

        if request.include_chronological:
            for previous, current in zip(
                ordered_events,
                ordered_events[1:],
            ):
                relationships.append(
                    CorrelationCandidate(
                        source_event_id=previous.event_id,
                        target_event_id=current.event_id,
                        relationship_type=(
                            EventRelationshipType.FOLLOWS
                        ),
                        confidence=1.0,
                        reason=(
                            "Events occurred consecutively "
                            "within the same session."
                        ),
                    )
                )

        if request.include_causal:
            for source in ordered_events:
                for target in ordered_events:
                    if source.event_id == target.event_id:
                        continue

                    if (
                        source.event_type
                        == EventType.PROMPT_INJECTION_DETECTED
                        and target.event_type
                        == EventType.SENSITIVE_ACTION_ATTEMPTED
                        and source.timestamp <= target.timestamp
                    ):
                        relationships.append(
                            CorrelationCandidate(
                                source_event_id=source.event_id,
                                target_event_id=target.event_id,
                                relationship_type=(
                                    EventRelationshipType.CAUSED_BY
                                ),
                                confidence=0.9,
                                reason=(
                                    "A sensitive action occurred "
                                    "after a detected prompt injection."
                                ),
                            )
                        )

                    if (
                        source.event_type
                        == EventType.POLICY_VIOLATION
                        and target.event_type
                        == EventType.TOOL_BLOCKED
                        and source.timestamp <= target.timestamp
                    ):
                        relationships.append(
                            CorrelationCandidate(
                                source_event_id=source.event_id,
                                target_event_id=target.event_id,
                                relationship_type=(
                                    EventRelationshipType.CAUSED_BY
                                ),
                                confidence=0.95,
                                reason=(
                                    "The tool was blocked after "
                                    "a policy violation."
                                ),
                            )
                        )

        deduplicated: list[CorrelationCandidate] = []
        seen: set[tuple[str, str, EventRelationshipType]] = set()

        for relationship in relationships:
            key = (
                relationship.source_event_id,
                relationship.target_event_id,
                relationship.relationship_type,
            )

            if key in seen:
                continue

            seen.add(key)
            deduplicated.append(relationship)

        result = CorrelationResult(
            session_id=session_id,
            relationships=deduplicated,
            event_count=len(events),
            relationship_count=len(deduplicated),
        )

        return CorrelationResponse(
            session_id=result.session_id,
            event_count=result.event_count,
            relationship_count=result.relationship_count,
            relationships=[
                {
                    "source_event_id": item.source_event_id,
                    "target_event_id": item.target_event_id,
                    "relationship_type": item.relationship_type,
                    "confidence": item.confidence,
                    "reason": item.reason,
                }
                for item in result.relationships
            ],
        )