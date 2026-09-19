"""
Shared Pydantic schemas used across the AgentTrace API.

These schemas intentionally stay presentation-agnostic so they can be
used by both PostgreSQL-backed local development and AWS-backed deployments.
"""

from __future__ import annotations

from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class APIModel(BaseModel):
    """Base Pydantic model for API-facing schemas."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class FlexibleAPIModel(BaseModel):
    """
    Base model for schemas that intentionally allow provider-specific
    extension fields.
    """

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class PaginationParams(APIModel):
    """Common pagination parameters."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=25, ge=1, le=100)


class PageResponse(BaseModel, Generic[T]):
    """Standard list response envelope required by the frontend."""

    model_config = ConfigDict(from_attributes=True)

    items: list[T]
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total: int = Field(ge=0)
    has_next: bool


class TimestampRange(APIModel):
    """Optional timestamp range used by filtering APIs."""

    from_: datetime | None = Field(default=None, alias="from")
    to: datetime | None = None


class HealthResponse(APIModel):
    """Standard health response."""

    status: str
    service: str
    environment: str
    timestamp: datetime


class ErrorDetail(APIModel):
    """Structured API error detail."""

    code: str
    message: str
    field: str | None = None


class ErrorResponse(APIModel):
    """Standard error envelope."""

    error: ErrorDetail


class MessageResponse(APIModel):
    """Simple message response."""

    message: str


class IDResponse(APIModel):
    """Simple resource ID response."""

    id: str


class AuditMetadata(FlexibleAPIModel):
    """
    Metadata attached to important audit records.

    Provider-specific information is intentionally allowed here because
    audit metadata may differ between local and AWS deployments.
    """
