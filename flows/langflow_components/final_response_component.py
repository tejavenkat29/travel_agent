"""LangFlow component: Final Response Agent.

The sink node: collects every upstream output and produces the structured
summary (Data) plus the natural-language Markdown (Message).
"""

from __future__ import annotations

import asyncio

from langflow.custom import Component
from langflow.io import DataInput, Output
from langflow.schema import Data
from langflow.schema.message import Message


class FinalResponseComponent(Component):
    display_name = "Final Response Agent"
    description = "Synthesize all agent outputs into JSON + a Markdown summary."
    icon = "file-text"
    name = "FinalResponseAgent"

    inputs = [
        DataInput(name="trip", display_name="Trip"),
        DataInput(name="flights", display_name="Flights", required=False),
        DataInput(name="hotel", display_name="Hotel", required=False),
        DataInput(name="weather", display_name="Weather", required=False),
        DataInput(name="budget", display_name="Budget", required=False),
    ]
    outputs = [
        Output(display_name="Summary (JSON)", name="summary", method="build_summary"),
        Output(display_name="Summary (Text)", name="text", method="build_text"),
    ]

    def _compose(self):
        from app.agents.final_response import (
            build_final_response_agent_from_settings,
        )
        from app.core.config import settings
        from app.schemas.budget import BudgetEstimate
        from app.schemas.flight import FlightOffer
        from app.schemas.hotel import HotelInfo
        from app.schemas.summary import FinalResponseRequest
        from app.schemas.trip import TripParameters
        from app.schemas.weather import WeatherAdvisory

        offers = (self.flights.data.get("offers") if self.flights else None) or []
        hotel_d = self.hotel.data.get("hotel") if self.hotel else None
        request = FinalResponseRequest(
            trip=TripParameters(**self.trip.data),
            flights=[FlightOffer(**o) for o in offers],
            hotel=HotelInfo(**hotel_d) if hotel_d else None,
            weather=WeatherAdvisory(**self.weather.data)
            if self.weather and self.weather.data
            else None,
            budget=BudgetEstimate(**self.budget.data) if self.budget else None,
        )
        agent = build_final_response_agent_from_settings(settings)
        return asyncio.run(agent.compose(request))

    def build_summary(self) -> Data:
        result = self._compose()
        return Data(data=result.summary.model_dump())

    def build_text(self) -> Message:
        result = self._compose()
        return Message(text=result.natural_language)
