"""LangFlow component: Flight Agent."""

from __future__ import annotations

import asyncio

from langflow.custom import Component
from langflow.io import DataInput, Output
from langflow.schema import Data


class FlightAgentComponent(Component):
    display_name = "Flight Agent"
    description = "Find flight offers for the trip (mock/real provider)."
    icon = "plane"
    name = "FlightAgent"

    inputs = [DataInput(name="trip", display_name="Trip", info="TripParameters")]
    outputs = [Output(display_name="Flights", name="flights", method="run_flights")]

    def run_flights(self) -> Data:
        from app.agents.flight import build_flight_agent_from_settings
        from app.core.config import settings
        from app.schemas.trip import TripParameters

        trip = TripParameters(**self.trip.data)
        offers = asyncio.run(
            build_flight_agent_from_settings(settings).find_flights(trip)
        )
        data = {"offers": [o.model_dump() for o in offers]}
        self.status = f"{len(offers)} offers"
        return Data(data=data)
