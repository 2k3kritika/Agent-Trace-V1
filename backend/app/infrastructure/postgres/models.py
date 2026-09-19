"""
SQLAlchemy persistence models for AgentTrace.

These models represent local PostgreSQL persistence. They are deliberately
kept in the infrastructure layer so domain logic remains database-agnostic.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""


class TimestampMixin:
    """Common created/updated timestamp fields."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class User(Base, TimestampMixin):
    """Application user."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    display_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(64),
        default="operator",
        nullable=False,
    )


class Agent(Base, TimestampMixin):
    """Monitored AI agent."""

    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    agent_id: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        index=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    provider: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
    )

    provider_display_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(32),
        default="OFFLINE",
        nullable=False,
        index=True,
    )

    risk_score: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    risk_level: Mapped[str] = mapped_column(
        String(32),
        default="LOW",
        nullable=False,
    )

    last_seen: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    integration_type: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    capabilities: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )


class Integration(Base, TimestampMixin):
    """Agent telemetry integration configuration."""

    __tablename__ = "integrations"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    agent_id: Mapped[str] = mapped_column(
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    integration_type: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    provider: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    endpoint: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    api_key_reference: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    environment: Mapped[str] = mapped_column(
        String(64),
        default="local",
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(64),
        default="DISCONNECTED",
        nullable=False,
    )

    configuration: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )


class Session(Base, TimestampMixin):
    """Monitored agent execution session."""

    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    session_id: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        index=True,
        nullable=False,
    )

    agent_id: Mapped[str] = mapped_column(
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    provider: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(64),
        default="ACTIVE",
        nullable=False,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    duration: Mapped[float | None] = mapped_column(
        nullable=True,
    )

    event_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    alert_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    risk_score: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    risk_level: Mapped[str] = mapped_column(
        String(32),
        default="LOW",
        nullable=False,
    )

    scenario: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    investigation_id: Mapped[str | None] = mapped_column(
        ForeignKey(
            "investigations.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
    )


class Investigation(Base, TimestampMixin):
    """Security investigation generated from one or more sessions/events."""

    __tablename__ = "investigations"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    session_id: Mapped[str | None] = mapped_column(
        ForeignKey("sessions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    agent_id: Mapped[str | None] = mapped_column(
        ForeignKey("agents.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(64),
        default="OPEN",
        nullable=False,
        index=True,
    )

    risk_score: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    risk_level: Mapped[str] = mapped_column(
        String(32),
        default="LOW",
        nullable=False,
    )

    scenario: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    verdict_type: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    attack_vector: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    impact: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )

    sensitive_action_attempted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    sensitive_action_executed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    policy_violation: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    action_blocked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    external_transmission: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    summary: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    graph: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )


class Event(Base, TimestampMixin):
    """Canonical AgentTrace event."""

    __tablename__ = "events"

    __table_args__ = (
        UniqueConstraint(
            "event_id",
            name="uq_events_event_id",
        ),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    event_id: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    session_id: Mapped[str] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    agent_id: Mapped[str] = mapped_column(
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    provider: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    event_type: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    tool: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    source: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    severity: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
        index=True,
    )

    details: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
    )

    parent_event_id: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        index=True,
    )

    related_event_id: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        index=True,
    )

    trace_id: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        index=True,
    )

    span_id: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        index=True,
    )


class Alert(Base, TimestampMixin):
    """Security alert generated by detection/correlation/policy processing."""

    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    alert_id: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        nullable=False,
        index=True,
    )

    agent_id: Mapped[str | None] = mapped_column(
        ForeignKey("agents.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    session_id: Mapped[str | None] = mapped_column(
        ForeignKey("sessions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    investigation_id: Mapped[str | None] = mapped_column(
        ForeignKey("investigations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    severity: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(32),
        default="OPEN",
        nullable=False,
        index=True,
    )

    detector_id: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
    )


class Evidence(Base, TimestampMixin):
    """Evidence item associated with an investigation."""

    __tablename__ = "evidence"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    investigation_id: Mapped[str] = mapped_column(
        ForeignKey("investigations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    event_id: Mapped[str | None] = mapped_column(
        ForeignKey("events.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    evidence_type: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    storage_uri: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    sha256: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    content: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
    )


class Policy(Base, TimestampMixin):
    """Security policy definition."""

    __tablename__ = "policies"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(32),
        default="ACTIVE",
        nullable=False,
    )

    action: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    priority: Mapped[int] = mapped_column(
        Integer,
        default=100,
        nullable=False,
    )

    rules: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
    )


class Report(Base, TimestampMixin):
    """Generated investigation report."""

    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    investigation_id: Mapped[str] = mapped_column(
        ForeignKey("investigations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    report_type: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(32),
        default="PENDING",
        nullable=False,
    )

    title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    storage_uri: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
    )
