"""LangFlow component: Weather Agent."""

from __future__ import annotations

import asyncio

from langflow.custom import Component
from langflow.io import DataInput, Output
from langflow.schema import Data


class WeatherAgentComponent(Component):
    display_name = "Weather Agent"
    description = "Forecast + clothing and best-time-to-visit advice."
    icon = "cloud-sun"
    name = "WeatherAgent"

    inputs = [DataInput(name="trip", display_name="Trip", info="TripParameters")]
    outputs = [Output(display_name="Weather", name="weather", method="run_weather")]

    def run_weather(self) -> Data:
        from app.agents.weather import build_weather_agent_from_settings
        from app.core.config import settings
        from app.schemas.trip import TripParameters

        trip = TripParameters(**self.trip.data)
        if not trip.destination:
            return Data(data={})
        advisory = asyncio.run(
            build_weather_agent_from_settings(settings).advise(trip.destination)
        )
        self.status = advisory.best_time_to_visit
        return Data(data=advisory.model_dump())
