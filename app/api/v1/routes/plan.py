"""Trip-planning endpoint — `POST /api/v1/plan`.

Runs the full LangGraph workflow end-to-end. The request can carry a flight the
user already has, a hotel they already booked, and a weather toggle — these are
seeded into the initial state so the conditional edge skips the matching agents.
"""

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from app.agents.graph.state import TravelState
from app.api.v1.dependencies import get_travel_workflow
from app.schemas.summary import FinalResponse, TripPlanRequest

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph

router = APIRouter(prefix="/plan", tags=["plan"])


@router.post(
    "",
    response_model=FinalResponse,
    summary="Plan a trip end-to-end via the LangGraph workflow",
    description="Runs planner → (flights, hotel, weather as needed) → budget → "
    "final_response. Skips flight/hotel/weather agents when the user already "
    "has that info.",
)
async def plan_trip(
    body: TripPlanRequest,
    workflow: "CompiledStateGraph" = Depends(get_travel_workflow),
) -> FinalResponse:
    # Seed the initial state. Pre-supplied flight/hotel both skip their agent
    # (via the router) and remain available to budget + final_response.
    initial: TravelState = {
        "user_request": body.request,
        "include_weather": body.include_weather,
    }
    if body.provided_flight is not None:
        initial["flights"] = [body.provided_flight]
    if body.provided_hotel is not None:
        initial["hotel"] = body.provided_hotel

    result = await workflow.ainvoke(initial)
    return result["final"]
