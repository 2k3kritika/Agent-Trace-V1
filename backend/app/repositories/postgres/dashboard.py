from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select

from app.infrastructure.postgres.models import (
    Agent,
    Alert,
    Event,
    Investigation,
    Session,
)
from app.core.constants import RiskLevel
from app.domain.events.types import EventSeverity


class PostgresDashboardRepository:
    def __init__(self, session):
        self.session = session

    async def count_agents(self) -> dict[str, int]:
        total_result = await self.session.execute(
            select(func.count(Agent.id))
        )

        active_result = await self.session.execute(
            select(func.count(Agent.id)).where(
                Agent.status == "ACTIVE"
            )
        )

        inactive_result = await self.session.execute(
            select(func.count(Agent.id)).where(
                Agent.status != "ACTIVE"
            )
        )

        high_result = await self.session.execute(
            select(func.count(Agent.id)).where(
                Agent.risk_level == RiskLevel.HIGH.value
            )
        )

        critical_result = await self.session.execute(
            select(func.count(Agent.id)).where(
                Agent.risk_level == RiskLevel.CRITICAL.value
            )
        )

        return {
            "total": total_result.scalar_one() or 0,
            "active": active_result.scalar_one() or 0,
            "inactive": inactive_result.scalar_one() or 0,
            "high_risk": high_result.scalar_one() or 0,
            "critical_risk": critical_result.scalar_one() or 0,
        }

    async def count_sessions(self) -> dict[str, int]:
        total_result = await self.session.execute(
            select(func.count(Session.id))
        )

        active_result = await self.session.execute(
            select(func.count(Session.id)).where(
                Session.status == "ACTIVE"
            )
        )

        completed_result = await self.session.execute(
            select(func.count(Session.id)).where(
                Session.status == "COMPLETED"
            )
        )

        return {
            "total": total_result.scalar_one() or 0,
            "active": active_result.scalar_one() or 0,
            "completed": completed_result.scalar_one() or 0,
        }

    async def count_investigations(self) -> dict[str, int]:
        total_result = await self.session.execute(
            select(func.count(Investigation.id))
        )

        open_result = await self.session.execute(
            select(func.count(Investigation.id)).where(
                Investigation.status == "OPEN"
            )
        )

        closed_result = await self.session.execute(
            select(func.count(Investigation.id)).where(
                Investigation.status == "CLOSED"
            )
        )

        high_result = await self.session.execute(
            select(func.count(Investigation.id)).where(
                Investigation.risk_level == RiskLevel.HIGH.value
            )
        )

        critical_result = await self.session.execute(
            select(func.count(Investigation.id)).where(
                Investigation.risk_level == RiskLevel.CRITICAL.value
            )
        )

        return {
            "total": total_result.scalar_one() or 0,
            "open": open_result.scalar_one() or 0,
            "closed": closed_result.scalar_one() or 0,
            "high_risk": high_result.scalar_one() or 0,
            "critical_risk": critical_result.scalar_one() or 0,
        }

    async def count_alerts(self) -> dict[str, int]:
        total_result = await self.session.execute(
            select(func.count(Alert.id))
        )

        open_result = await self.session.execute(
            select(func.count(Alert.id)).where(
                Alert.status == "OPEN"
            )
        )

        acknowledged_result = await self.session.execute(
            select(func.count(Alert.id)).where(
                Alert.status == "ACKNOWLEDGED"
            )
        )

        resolved_result = await self.session.execute(
            select(func.count(Alert.id)).where(
                Alert.status == "RESOLVED"
            )
        )

        critical_result = await self.session.execute(
            select(func.count(Alert.id)).where(
                Alert.severity == EventSeverity.CRITICAL.value
            )
        )

        high_result = await self.session.execute(
            select(func.count(Alert.id)).where(
                Alert.severity == EventSeverity.HIGH.value
            )
        )

        return {
            "total": total_result.scalar_one() or 0,
            "open": open_result.scalar_one() or 0,
            "acknowledged": acknowledged_result.scalar_one() or 0,
            "resolved": resolved_result.scalar_one() or 0,
            "critical": critical_result.scalar_one() or 0,
            "high": high_result.scalar_one() or 0,
        }

    async def risk_distribution(self) -> dict[str, int]:
        result = await self.session.execute(
            select(
                Investigation.risk_level,
                func.count(Investigation.id),
            ).group_by(
                Investigation.risk_level
            )
        )

        distribution = {
            "low": 0,
            "medium": 0,
            "high": 0,
            "critical": 0,
        }

        for risk_level, count in result.all():
            if risk_level:
                key = str(risk_level).lower()

                if key in distribution:
                    distribution[key] = count or 0

        return distribution

    async def recent_security_events(
        self,
        limit: int = 10,
    ) -> list[Event]:
        result = await self.session.execute(
            select(Event)
            .where(
                Event.severity.in_(
                    [
                        EventSeverity.MEDIUM.value,
                        EventSeverity.HIGH.value,
                        EventSeverity.CRITICAL.value,
                    ]
                )
            )
            .order_by(
                Event.timestamp.desc()
            )
            .limit(limit)
        )

        return list(result.scalars().all())