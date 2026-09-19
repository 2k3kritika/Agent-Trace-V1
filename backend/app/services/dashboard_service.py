from __future__ import annotations

from typing import Any


class DashboardService:
    def __init__(
        self,
        dashboard_repository: Any,
    ) -> None:
        self.dashboard_repository = dashboard_repository

    async def get_overview(
        self,
        recent_limit: int = 10,
    ) -> dict[str, Any]:
        (
            agents,
            sessions,
            investigations,
            alerts,
            security_events_last_24h,
            risk_distribution,
            recent_security_events,
        ) = await self._collect_metrics(recent_limit)

        return {
            "agents": agents,
            "sessions": sessions,
            "investigations": investigations,
            "alerts": alerts,
            "security_events_last_24h": security_events_last_24h,
            "risk_distribution": risk_distribution,
            "recent_security_events": recent_security_events,
        }

    async def _collect_metrics(
        self,
        recent_limit: int,
    ) -> tuple[
        int,
        int,
        int,
        int,
        int,
        dict[str, int],
        list[dict[str, Any]],
    ]:
        repository = self.dashboard_repository

        agents = await repository.count_agents()
        sessions = await repository.count_sessions()
        investigations = await repository.count_investigations()
        alerts = await repository.count_alerts()
        security_events_last_24h = (
            await repository.count_security_events_last_24h()
        )
        risk_distribution = await repository.risk_distribution()
        recent_security_events = (
            await repository.recent_security_events(recent_limit)
        )

        return (
            agents,
            sessions,
            investigations,
            alerts,
            security_events_last_24h,
            risk_distribution,
            recent_security_events,
        )