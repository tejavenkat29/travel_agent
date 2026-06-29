"""Budget endpoint — `POST /api/v1/budget/estimate`.

Takes the travel state (plus optional actual costs / rate overrides) and returns
a structured cost breakdown compared against the user's budget.
"""

from fastapi import APIRouter, Depends

from app.agents.budget import BudgetAgent
from app.api.v1.dependencies import get_budget_agent
from app.schemas.budget import BudgetEstimate, BudgetRequest

router = APIRouter(prefix="/budget", tags=["budget"])


@router.post(
    "/estimate",
    response_model=BudgetEstimate,
    summary="Estimate trip cost and compare to budget",
    description="Calculates flight, hotel, food and transport costs, totals "
    "them, and compares against the user's budget.",
)
async def estimate_budget(
    body: BudgetRequest,
    agent: BudgetAgent = Depends(get_budget_agent),
) -> BudgetEstimate:
    return await agent.estimate(
        body.trip,
        transport_total=body.transport_total,
        hotel_per_night=body.hotel_per_night,
        rates=body.rates,
    )
