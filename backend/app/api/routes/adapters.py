from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.adapters.factory import default_registry
from app.schemas.common import APIModel
from app.services.adapter_service import AdapterService
from app.services.dependency import get_event_service


router = APIRouter(
    prefix="/adapters",
    tags=["adapters"],
)


class AdapterSummary(APIModel):
    name: str
    provider: str
    display_name: str


class AdapterListResponse(APIModel):
    items: list[AdapterSummary]
    total: int


class AdapterEventRequest(APIModel):
    event: dict[str, Any]
    agent_id: str | None = None
    session_id: str | None = None


class AdapterBatchRequest(APIModel):
    events: list[dict[str, Any]]
    agent_id: str | None = None
    session_id: str | None = None


class AdapterHealthResponse(APIModel):
    adapter: str
    provider: str
    healthy: bool
    message: str


def get_adapter_service(
    event_service=Depends(get_event_service),
) -> AdapterService:
    return AdapterService(
        registry=default_registry,
        event_service=event_service,
    )


@router.get("", response_model=AdapterListResponse)
async def list_adapters(
    service: AdapterService = Depends(get_adapter_service),
) -> AdapterListResponse:
    adapters: list[AdapterSummary] = []

    for adapter_name in service.list_adapters():
        adapter = service.get_adapter(adapter_name)

        adapters.append(
            AdapterSummary(
                name=adapter.name,
                provider=adapter.provider,
                display_name=adapter.display_name,
            )
        )

    return AdapterListResponse(
        items=adapters,
        total=len(adapters),
    )


@router.get(
    "/{adapter_name}/health",
    response_model=AdapterHealthResponse,
)
async def adapter_health(
    adapter_name: str,
    service: AdapterService = Depends(get_adapter_service),
) -> AdapterHealthResponse:
    try:
        result = service.health_check(adapter_name)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Adapter '{adapter_name}' is not registered.",
        ) from exc

    return AdapterHealthResponse(
        adapter=result.adapter,
        provider=result.provider,
        healthy=result.healthy,
        message=result.message,
    )


@router.post(
    "/{adapter_name}/events",
    status_code=status.HTTP_201_CREATED,
)
async def ingest_adapter_event(
    adapter_name: str,
    request: AdapterEventRequest,
    service: AdapterService = Depends(get_adapter_service),
):
    try:
        return await service.ingest_event(
            adapter_name,
            request.event,
            default_agent_id=request.agent_id,
            default_session_id=request.session_id,
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Adapter '{adapter_name}' is not registered.",
        ) from exc


@router.post(
    "/{adapter_name}/events/batch",
    status_code=status.HTTP_201_CREATED,
)
async def ingest_adapter_events(
    adapter_name: str,
    request: AdapterBatchRequest,
    service: AdapterService = Depends(get_adapter_service),
    continue_on_error: bool = Query(default=False),
):
    if not request.events:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one event is required.",
        )

    try:
        if continue_on_error:
            results: list[Any] = []

            for event in request.events:
                try:
                    result = await service.ingest_event(
                        adapter_name,
                        event,
                        default_agent_id=request.agent_id,
                        default_session_id=request.session_id,
                    )
                    results.append(result)
                except Exception as exc:
                    results.append(
                        {
                            "success": False,
                            "error": str(exc),
                        }
                    )

            return {
                "adapter": adapter_name,
                "items": results,
                "total": len(results),
            }

        results = await service.ingest_events(
            adapter_name,
            request.events,
            default_agent_id=request.agent_id,
            default_session_id=request.session_id,
        )

        return {
            "adapter": adapter_name,
            "items": results,
            "total": len(results),
        }

    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Adapter '{adapter_name}' is not registered.",
        ) from exc