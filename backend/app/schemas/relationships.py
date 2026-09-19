from datetime import datetime
from typing import Any

from pydantic import Field

from app.domain.events.types import EventRelationshipType
from app.schemas.common import APIModel


class EventRelationshipCreateRequest(APIModel):
    source_event_id: str
    target_event_id: str
    relationship_type: EventRelationshipType
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    reason: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class EventRelationshipResponse(APIModel):
    source_event_id: str
    target_event_id: str
    relationship_type: EventRelationshipType
    confidence: float
    reason: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime | None = None