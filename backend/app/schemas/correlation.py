from app.domain.events.types import EventRelationshipType
from app.schemas.common import APIModel
from pydantic import Field


class CorrelationRequest(APIModel):
    include_chronological: bool = True
    include_causal: bool = True


class CorrelationRelationshipResponse(APIModel):
    source_event_id: str
    target_event_id: str
    relationship_type: EventRelationshipType
    confidence: float
    reason: str


class CorrelationResponse(APIModel):
    session_id: str
    event_count: int
    relationship_count: int

    relationships: list[CorrelationRelationshipResponse] = Field(default_factory=list)
