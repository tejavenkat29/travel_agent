"""LangFlow component: Budget Agent.

Joins the flight and hotel outputs (optional inputs ≈ the LangGraph conditional
skip) and estimates total cost vs. the user's budget.
"""

from __future__ import annotations

import asyncio

from langflow.custom import Component
from langflow.io import DataInput, Output
from langflow.schema import Data


class BudgetAgentComponent(Component):
    display_name = "Budget Agent"
    description = "Estimate trip cost and compare to budget."
    icon = "calculator"
    name = "BudgetAgent"

    inputs = [
        DataInput(name="trip", display_name="Trip", info="TripParameters"),
        DataInput(name="flights", display_name="Flights", required=False),
        DataInput(name="hotel", display_name="Hotel", required=False),
    ]
    outputs = [Output(display_name="Budget", name="budget", method="run_budget")]

    def run_budget(self) -> Data:
        from app.agents.budget import BudgetAgent
        from app.schemas.trip import TripParameters

        trip = TripParameters(**self.trip.data)

        offers = (self.flights.data.get("offers") if self.flights else None) or []
        flight_total = min((o["total_price"] for o in offers), default=None)

        hotel = self.hotel.data.get("hotel") if self.hotel else None
        hotel_nightly = hotel["nightly_rate"] if hotel else None

        estimate = asyncio.run(
            BudgetAgent().estimate(
                trip, flight_total=flight_total, hotel_per_night=hotel_nightly
            )
        )
        self.status = estimate.summary
        return Data(data=estimate.model_dump())
