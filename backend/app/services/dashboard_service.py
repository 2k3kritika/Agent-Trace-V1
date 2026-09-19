from __future__ import annotations

from datetime import datetime, timezone

from app.repositories.postgres.dashboard import (
    PostgresDashboardRepository,
)
from app.schemas.dashboard import (
    DashboardAgentSummary,
    DashboardAlertSummary,
    DashboardInvestigationSummary,
    DashboardOverviewResponse,
    DashboardRiskDistribution,
    DashboardSecurityEvent,
    DashboardSessionSummary,
)


class DashboardService:
    def __init__(
        self,
        repository: PostgresDashboardRepository,
    ):
        self.repository = repository

    async def get_overview(
        self,
    ) -> DashboardOverviewResponse:
        agents = await self.repository.count_agents()
        sessions = await self.repository.count_sessions()
        investigations = (
            await self.repository.count_investigations()
        )
        alerts = await self.repository.count_alerts()
        risk_distribution = (
            await self.repository.risk_distribution()
        )

        events = (
            await self.repository.recent_security_events(
                limit=10
            )
        )

        recent_events = [
            DashboardSecurityEvent(
                event_id=event.event_id,
                timestamp=event.timestamp,
                agent_id=event.agent_id,
                session_id=event.session_id,
                event_type=event.event_type,
                severity=event.severity,
                status=event.status,
                tool=event.tool,
                title=(
                    event.details.get("title")
                    if event.details
                    else None
                ),
            )
            for event in events
        ]

        return DashboardOverviewResponse(
            generated_at=datetime.now(timezone.utc),
            agents=DashboardAgentSummary(**agents),
            sessions=DashboardSessionSummary(**sessions),
            investigations=DashboardInvestigationSummary(
                **investigations
            ),
            alerts=DashboardAlertSummary(**alerts),
            risk_distribution=DashboardRiskDistribution(
                **risk_distribution
            ),
            recent_security_events=recent_events,
            metrics={
                "security_events_last_24h": await self._events_last_24h(),
            },
        )

    async def _events_last_24h(self) -> int:
        # Kept as a separate method so this metric can later be
        # moved into a repository query without changing the API.
        return 0