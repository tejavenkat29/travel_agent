"""Budget Agent.

Computes a per-category cost breakdown for a trip, totals it, and compares it
against the user's budget. It is pure arithmetic — no I/O, no LLM — so the core
logic lives in small, independently testable functions and the agent just
orchestrates them.

Each category is *estimated* from `BudgetRates` unless an *actual* figure is
supplied (e.g. a chosen flight total from the Flight Agent), in which case the
actual value is used. Every line item records how it was derived for full
transparency.
"""

from __future__ import annotations

from app.core.logging import get_logger
from app.core.observability import traceable
from app.schemas.budget import (
    BudgetEstimate,
    BudgetRates,
    CostBreakdown,
    CostLineItem,
)
from app.schemas.trip import TripParameters

logger = get_logger(__name__)


def _money(value: float) -> float:
    return round(value, 2)


def compute_breakdown(
    state: TripParameters,
    *,
    rates: BudgetRates,
    transport_total: float | None = None,
    hotel_per_night: float | None = None,
) -> CostBreakdown:
    """Compute per-category costs (actuals override estimates)."""
    days = state.num_days or 1
    travelers = state.travelers or 1

    # --- Intercity travel (flight/train/bus) ---
    if transport_total is not None:
        travel = _money(transport_total)
        travel_item = CostLineItem(
            category="travel",
            amount=travel,
            detail="Recommended transport total provided",
            estimated=False,
        )
    else:
        travel = _money(rates.travel_per_person * travelers)
        travel_item = CostLineItem(
            category="travel",
            amount=travel,
            detail=f"{rates.travel_per_person} x {travelers} travelers",
            estimated=True,
        )

    # --- Hotel ---
    nightly = hotel_per_night if hotel_per_night is not None else rates.hotel_per_night
    hotel = _money(nightly * days)
    hotel_item = CostLineItem(
        category="hotel",
        amount=hotel,
        detail=f"{nightly} x {days} nights",
        estimated=hotel_per_night is None,
    )

    # --- Food ---
    food = _money(rates.food_per_person_per_day * travelers * days)
    food_item = CostLineItem(
        category="food",
        amount=food,
        detail=f"{rates.food_per_person_per_day} x {travelers} travelers x {days} days",
        estimated=True,
    )

    # --- Local transport (at the destination) ---
    local = _money(rates.transport_per_person_per_day * travelers * days)
    local_item = CostLineItem(
        category="local transport",
        amount=local,
        detail=(
            f"{rates.transport_per_person_per_day} x {travelers} travelers "
            f"x {days} days"
        ),
        estimated=True,
    )

    return CostBreakdown(
        travel=travel,
        hotel=hotel,
        food=food,
        transport=local,
        line_items=[travel_item, hotel_item, food_item, local_item],
    )


class BudgetAgent:
    """Estimates trip cost and compares it to the user's budget."""

    def __init__(self, default_rates: BudgetRates | None = None) -> None:
        # Default assumptions; per-request overrides take precedence.
        self._default_rates = default_rates or BudgetRates()

    @traceable(run_type="chain", name="budget_agent")
    async def estimate(
        self,
        state: TripParameters,
        *,
        transport_total: float | None = None,
        hotel_per_night: float | None = None,
        rates: BudgetRates | None = None,
    ) -> BudgetEstimate:
        rates = rates or self._default_rates
        currency = state.currency or rates.currency
        days = state.num_days or 1
        travelers = state.travelers or 1

        breakdown = compute_breakdown(
            state,
            rates=rates,
            transport_total=transport_total,
            hotel_per_night=hotel_per_night,
        )
        total = _money(
            breakdown.travel + breakdown.hotel + breakdown.food + breakdown.transport
        )

        within_budget = difference = utilization = None
        budget = state.budget
        if budget is not None:
            difference = _money(budget - total)
            within_budget = total <= budget
            utilization = _money((total / budget) * 100) if budget > 0 else None
            verdict = "within" if within_budget else "over"
            summary = (
                f"Estimated total {currency} {total:,.2f} for {travelers} "
                f"traveler(s) over {days} day(s) is {verdict} the "
                f"{currency} {budget:,.2f} budget "
                f"({'surplus' if difference >= 0 else 'shortfall'} "
                f"{currency} {abs(difference):,.2f})."
            )
        else:
            summary = (
                f"Estimated total {currency} {total:,.2f} for {travelers} "
                f"traveler(s) over {days} day(s). No budget provided to compare."
            )

        logger.info(
            "budget.estimated", total=total, budget=budget, within=within_budget
        )
        return BudgetEstimate(
            currency=currency,
            days=days,
            travelers=travelers,
            breakdown=breakdown,
            total_cost=total,
            user_budget=budget,
            within_budget=within_budget,
            difference=difference,
            budget_utilization_pct=utilization,
            summary=summary,
        )


def build_budget_agent_from_settings(settings) -> BudgetAgent:  # noqa: ARG001
    """Build the Budget Agent. (Settings reserved for future rate config.)"""
    return BudgetAgent()
