"""Weather provider factory.

Centralises the `WeatherProvider` choice: live API when `WEATHER_API_KEY` is
configured, otherwise the deterministic mock. The agent only ever sees the
`WeatherProvider` abstraction.
"""

from __future__ import annotations

from app.core.config import Settings
from app.core.logging import get_logger
from app.domain.interfaces.weather import WeatherProvider
from app.infrastructure.external.weather.mock_provider import MockWeatherProvider

logger = get_logger(__name__)


def build_weather_provider(settings: Settings) -> WeatherProvider:
    """Return the configured weather provider (live if keyed, else mock)."""
    if settings.WEATHER_API_KEY:
        from app.infrastructure.external.weather.api_provider import (
            ApiWeatherProvider,
        )

        logger.info("weather.provider_selected", provider="api")
        return ApiWeatherProvider(api_key=settings.WEATHER_API_KEY)

    logger.info("weather.provider_selected", provider="mock")
    return MockWeatherProvider()
