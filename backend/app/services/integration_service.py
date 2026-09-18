from __future__ import annotations

from typing import Any

from app.infrastructure.postgres.models import Integration
from app.repositories.interfaces import (
    IntegrationRepository,
    RepositoryListResult,
)


class IntegrationService:
    """Application service for telemetry/tool integrations."""

    def __init__(
        self,
        repository: IntegrationRepository,
    ) -> None:
        self.repository = repository

    async def get_integration(
        self,
        integration_id: str,
    ) -> Integration:
        return await self.repository.get_by_id(
            integration_id
        )

    async def create_integration(
        self,
        *,
        agent_id: str,
        integration_type: str,
        provider: str,
        endpoint: str | None = None,
        api_key_reference: str | None = None,
        environment: str | None = None,
        status: str = "active",
        configuration: dict[str, Any] | None = None,
    ) -> Integration:
        integration = Integration(
            agent_id=agent_id,
            integration_type=integration_type,
            provider=provider,
            endpoint=endpoint,
            api_key_reference=api_key_reference,
            environment=environment,
            status=status,
            configuration=configuration or {},
        )

        return await self.repository.create(
            integration
        )

    async def update_integration(
        self,
        integration_id: str,
        *,
        status: str | None = None,
        endpoint: str | None = None,
        environment: str | None = None,
        configuration: dict[str, Any] | None = None,
    ) -> Integration:
        integration = await self.repository.get_by_id(
            integration_id
        )

        if status is not None:
            integration.status = status

        if endpoint is not None:
            integration.endpoint = endpoint

        if environment is not None:
            integration.environment = environment

        if configuration is not None:
            integration.configuration = configuration

        return await self.repository.update(
            integration
        )

    async def delete_integration(
        self,
        integration_id: str,
    ) -> None:
        await self.repository.delete(
            integration_id
        )

    async def list_integrations(
        self,
        *,
        page: int = 1,
        page_size: int = 25,
        agent_id: str | None = None,
        status: str | None = None,
        provider: str | None = None,
        integration_type: str | None = None,
    ) -> RepositoryListResult[Integration]:
        return await self.repository.list(
            page=page,
            page_size=page_size,
            agent_id=agent_id,
            status=status,
            provider=provider,
            integration_type=integration_type,
        )