from __future__ import annotations

from datetime import datetime

from app.domain.events.types import EventRelationshipType
from app.schemas.common import APIModel
from pydantic import Field


class CorrelationCandidate(APIModel):
    source_event_id: str
    target_event_id: str

    relationship_type: EventRelationshipType

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    reason: str

    created_at: datetime | None = None


class CorrelationResult(APIModel):
    session_id: str

    relationships: list[CorrelationCandidate] = Field(default_factory=list)

    event_count: int = 0
    relationship_count: int = 0
