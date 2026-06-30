"""Budget schemas — rate assumptions, request, and structured estimate.

The Budget Agent is a calculator, so its "configuration" is a set of **rate
assumptions** (`BudgetRates`) that are injectable and overridable — that is the
reuse seam (different markets/seasons just pass different rates). Actual figures
from other agents (a chosen flight total, a real hotel nightly rate) can be
passed in to *override* the estimates, so the same agent serves both a quick
standalone estimate and a precise pipeline calculation.
"""

from pydantic import BaseModel, Field

from app.schemas.trip import TripParameters


class BudgetRates(BaseModel):
    """Per-unit cost assumptions used when actual figures aren't supplied."""

    # Defaults are indicative INR figures (used only when an actual value isn't
    # supplied by the transport/hotel agents).
    travel_per_person: float = Field(
        default=2000.0,
        ge=0,
        description="Estimated intercity travel (flight/train/bus) per person",
    )
    hotel_per_night: float = Field(
        default=2500.0, ge=0, description="Estimated room cost per night"
    )
    food_per_person_per_day: float = Field(
        default=800.0, ge=0, description="Estimated food cost per person per day"
    )
    transport_per_person_per_day: float = Field(
        default=400.0, ge=0, description="Estimated local transport per person/day"
    )
    currency: str = Field(default="INR", description="Currency of these rates")


class BudgetRequest(BaseModel):
    """Input for the budget endpoint."""

    trip: TripParameters = Field(..., description="Shared travel state")
    transport_total: float | None = Field(
        default=None,
        ge=0,
        description="Actual intercity travel total (e.g. from the Transport Agent)",
    )
    hotel_per_night: float | None = Field(
        default=None, ge=0, description="Actual nightly hotel rate, if known"
    )
    rates: BudgetRates | None = Field(
        default=None, description="Override the default rate assumptions"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "trip": {
                    "destination": "Tokyo",
                    "source": "Mumbai",
                    "budget": 4000,
                    "currency": "USD",
                    "num_days": 5,
                    "travelers": 2,
                },
                "transport_total": 900,
            }
        }
    }


class CostLineItem(BaseModel):
    """One cost category with a transparent explanation of the math."""

    category: str = Field(..., description="Cost category")
    amount: float = Field(..., description="Computed amount")
    detail: str = Field(..., description="How the amount was derived")
    estimated: bool = Field(
        ..., description="True if estimated from rates, False if an actual figure"
    )


class CostBreakdown(BaseModel):
    """Per-category costs."""

    travel: float  # intercity travel (flight/train/bus)
    hotel: float
    food: float
    transport: float  # local transport at the destination
    line_items: list[CostLineItem]


class BudgetEstimate(BaseModel):
    """Structured budget estimate — the agent's output."""

    currency: str
    days: int
    travelers: int
    breakdown: CostBreakdown
    total_cost: float
    user_budget: float | None
    within_budget: bool | None = Field(
        default=None, description="Whether total_cost fits the user budget"
    )
    difference: float | None = Field(
        default=None, description="budget - total (positive = surplus, negative = over)"
    )
    budget_utilization_pct: float | None = Field(
        default=None, description="total_cost as a percentage of the budget"
    )
    summary: str = Field(..., description="Human-readable verdict")
