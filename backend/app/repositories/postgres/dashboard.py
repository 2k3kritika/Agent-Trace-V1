from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from app.infrastructure.postgres.models import (
    Agent,
    Alert,
    Event,
    Investigation,
    Session,
)
from app.infrastructure.postgres.session import session_scope
from sqlalchemy import func, select


class PostgresDashboardRepository:
    async def count_agents(self) -> int:
        async with session_scope() as db:
            result = await db.execute(select(func.count()).select_from(Agent))
            return int(result.scalar_one())

    async def count_sessions(self) -> int:
        async with session_scope() as db:
            result = await db.execute(select(func.count()).select_from(Session))
            return int(result.scalar_one())

    async def count_investigations(self) -> int:
        async with session_scope() as db:
            result = await db.execute(select(func.count()).select_from(Investigation))
            return int(result.scalar_one())

    async def count_alerts(self) -> int:
        async with session_scope() as db:
            result = await db.execute(select(func.count()).select_from(Alert))
            return int(result.scalar_one())

    async def count_security_events_last_24h(self) -> int:
        since = datetime.now(timezone.utc) - timedelta(hours=24)

        async with session_scope() as db:
            result = await db.execute(
                select(func.count())
                .select_from(Event)
                .where(
                    Event.timestamp >= since,
                    Event.event_type.in_(
                        [
                            "UNTRUSTED_CONTENT",
                            "PROMPT_INJECTION_DETECTED",
                            "SENSITIVE_ACTION_ATTEMPTED",
                            "POLICY_VIOLATION",
                            "TOOL_BLOCKED",
                        ]
                    ),
                )
            )

            return int(result.scalar_one())

    async def risk_distribution(self) -> dict[str, int]:
        async with session_scope() as db:
            result = await db.execute(
                select(
                    Investigation.risk_level,
                    func.count(Investigation.id),
                ).group_by(Investigation.risk_level)
            )

            return {
                str(level): int(count)
                for level, count in result.all()
                if level is not None
            }

    async def recent_security_events(
        self,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        async with session_scope() as db:
            result = await db.execute(
                select(Event)
                .where(
                    Event.event_type.in_(
                        [
                            "UNTRUSTED_CONTENT",
                            "PROMPT_INJECTION_DETECTED",
                            "SENSITIVE_ACTION_ATTEMPTED",
                            "POLICY_VIOLATION",
                            "TOOL_BLOCKED",
                        ]
                    )
                )
                .order_by(Event.timestamp.desc())
                .limit(limit)
            )

            events = result.scalars().all()

            return [
                {
                    "event_id": event.event_id,
                    "timestamp": event.timestamp,
                    "event_type": event.event_type,
                    "severity": event.severity,
                    "agent_id": event.agent_id,
                    "session_id": event.session_id,
                    "tool": event.tool,
                }
                for event in events
            ]
