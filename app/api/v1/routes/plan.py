"""Trip-planning endpoint — `POST /api/v1/plan`.

Runs the full LangGraph workflow end-to-end: a single natural-language request
flows through every agent node and returns the composed final summary.
"""

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from app.api.v1.dependencies import get_travel_workflow
from app.schemas.summary import FinalResponse
from app.schemas.trip import PlanRequest

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph

router = APIRouter(prefix="/plan", tags=["plan"])


@router.post(
    "",
    response_model=FinalResponse,
    summary="Plan a trip end-to-end via the LangGraph workflow",
    description="Runs planner → flights → weather → budget → final_response "
    "and returns the final structured + natural-language summary.",
)
async def plan_trip(
    body: PlanRequest,
    workflow: "CompiledStateGraph" = Depends(get_travel_workflow),
) -> FinalResponse:
    result = await workflow.ainvoke({"user_request": body.request})
    return result["final"]
