"""Weather provider port (interface).

The abstraction the Weather Agent depends on. The mock and any future real API
(OpenWeatherMap, WeatherAPI, ...) implement this one method, so they are fully
interchangeable and a new provider is added without touching the agent
(Open/Closed + Dependency Inversion).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas.weather import WeatherForecast


class WeatherProvider(ABC):
    """Source of raw weather data for a destination."""

    @abstractmethod
    async def get_forecast(self, destination: str) -> WeatherForecast:
        """Return the raw weather forecast for a destination."""
        raise NotImplementedError
