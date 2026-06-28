"""Planner endpoint — `POST /api/v1/planner/extract`.

Thin handler: hands the raw request to the `PlannerAgent` and returns the
structured `TripParameters` brief.
"""

from fastapi import APIRouter, Depends

from app.agents.planner import PlannerAgent
from app.api.v1.dependencies import get_planner_agent
from app.schemas.trip import PlanRequest, TripParameters

router = APIRouter(prefix="/planner", tags=["planner"])


@router.post(
    "/extract",
    response_model=TripParameters,
    summary="Extract structured trip parameters from a request",
    description="Runs the Planner Agent (LangChain structured output) to "
    "extract destination, source, budget, days and travelers.",
)
async def extract_trip_parameters(
    body: PlanRequest,
    agent: PlannerAgent = Depends(get_planner_agent),
) -> TripParameters:
    return await agent.plan(body.request)
