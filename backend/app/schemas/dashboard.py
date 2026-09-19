from datetime import datetime
from typing import Any

from pydantic import Field

from app.schemas.common import APIModel


class DashboardRiskDistribution(APIModel):
    low: int = 0
    medium: int = 0
    high: int = 0
    critical: int = 0


class DashboardAlertSummary(APIModel):
    total: int = 0
    open: int = 0
    acknowledged: int = 0
    resolved: int = 0
    critical: int = 0
    high: int = 0


class DashboardInvestigationSummary(APIModel):
    total: int = 0
    open: int = 0
    closed: int = 0
    high_risk: int = 0
    critical_risk: int = 0


class DashboardAgentSummary(APIModel):
    total: int = 0
    active: int = 0
    inactive: int = 0
    high_risk: int = 0
    critical_risk: int = 0


class DashboardSessionSummary(APIModel):
    total: int = 0
    active: int = 0
    completed: int = 0


class DashboardSecurityEvent(APIModel):
    event_id: str
    timestamp: datetime
    agent_id: str
    session_id: str | None = None
    event_type: str
    severity: str
    status: str
    tool: str | None = None
    title: str | None = None


class DashboardOverviewResponse(APIModel):
    generated_at: datetime

    agents: DashboardAgentSummary
    sessions: DashboardSessionSummary
    investigations: DashboardInvestigationSummary
    alerts: DashboardAlertSummary
    risk_distribution: DashboardRiskDistribution

    recent_security_events: list[DashboardSecurityEvent] = Field(
        default_factory=list
    )

    metrics: dict[str, Any] = Field(
        default_factory=dict
    )