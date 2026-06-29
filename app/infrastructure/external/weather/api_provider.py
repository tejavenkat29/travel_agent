"""Real weather-API provider (skeleton).

Placeholder `WeatherProvider` for a live weather service (e.g. OpenWeatherMap,
WeatherAPI.com). Demonstrates Open/Closed: implement `get_forecast()` here and
select it in the factory — the agent, endpoint and schemas stay unchanged.

Note: live current-weather endpoints return today's conditions; the seasonal
`SeasonOutlook` (for best-time-to-visit) would come from the provider's
climate/historical endpoint or a static climate dataset.
"""

from __future__ import annotations

import httpx

from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger
from app.domain.interfaces.weather import WeatherProvider
from app.schemas.weather import WeatherForecast

logger = get_logger(__name__)


class ApiWeatherProvider(WeatherProvider):
    """Fetches live weather from an external API."""

    def __init__(
        self, api_key: str, base_url: str = "https://api.openweathermap.org"
    ):
        self._api_key = api_key
        self._base_url = base_url

    async def get_forecast(self, destination: str) -> WeatherForecast:
        # TODO: implement the real integration. Intended shape:
        #
        # async with httpx.AsyncClient(base_url=self._base_url) as client:
        #     resp = await client.get(
        #         "/data/2.5/weather",
        #         params={"q": destination, "units": "metric",
        #                 "appid": self._api_key},
        #     )
        #     resp.raise_for_status()
        #     return _to_forecast(destination, resp.json())
        #
        # Only the payload->WeatherForecast mapping lives here; the agent that
        # derives clothing/best-time advice is untouched.
        _ = httpx  # make the intended dependency explicit
        raise ExternalServiceError(
            "Live weather API provider is not implemented yet.",
            code="weather_provider_unavailable",
        )
