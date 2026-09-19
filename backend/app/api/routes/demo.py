from __future__ import annotations

from fastapi import APIRouter, Depends

from app.schemas.demo import DemoRunResponse
from app.services.demo_scenario_service import DemoScenarioService
from app.services.dependency import get_demo_scenario_service

router = APIRouter(
    prefix="/demo",
    tags=["demo"],
)


@router.post(
    "/hero",
    response_model=DemoRunResponse,
)
async def run_hero_demo(
    service: DemoScenarioService = Depends(get_demo_scenario_service),
) -> DemoRunResponse:
    result = await service.run()

    return DemoRunResponse.model_validate(result)
