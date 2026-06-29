"""LangFlow component: Hotel Agent."""

from __future__ import annotations

import asyncio

from langflow.custom import Component
from langflow.io import DataInput, Output
from langflow.schema import Data


class HotelAgentComponent(Component):
    display_name = "Hotel Agent"
    description = "Find and recommend a hotel for the trip."
    icon = "bed"
    name = "HotelAgent"

    inputs = [DataInput(name="trip", display_name="Trip", info="TripParameters")]
    outputs = [Output(display_name="Hotel", name="hotel", method="run_hotel")]

    def run_hotel(self) -> Data:
        from app.agents.hotel import build_hotel_agent_from_settings
        from app.core.config import settings
        from app.schemas.trip import TripParameters

        trip = TripParameters(**self.trip.data)
        selected = asyncio.run(
            build_hotel_agent_from_settings(settings).find_hotel(trip)
        )
        data = {"hotel": selected.model_dump() if selected else None}
        self.status = selected.name if selected else "no hotel"
        return Data(data=data)
