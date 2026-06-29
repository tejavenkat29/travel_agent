"""Mock weather provider.

Implements `WeatherProvider` with deterministic, synthetic climate data derived
from the destination name — no API key, stable and testable output. Returns
only *facts* (current conditions + seasonal climatology); interpretation is the
agent's job.
"""

from __future__ import annotations

from app.core.logging import get_logger
from app.domain.interfaces.weather import WeatherProvider
from app.schemas.weather import SeasonOutlook, WeatherForecast

logger = get_logger(__name__)

_CONDITIONS = ["Sunny", "Partly cloudy", "Cloudy", "Light rain", "Humid & warm"]
# (season, mean-temperature offset from the annual mean, note)
_SEASONS = [
    ("Spring", 2, "Mild and pleasant, occasional showers"),
    ("Summer", 8, "Warmest period, busiest with tourists"),
    ("Autumn", 0, "Cooling down, fewer crowds"),
    ("Winter", -8, "Coldest period, lowest prices"),
]


def _seed(destination: str) -> int:
    """Stable pseudo-climate seed from the destination text."""
    return sum(ord(c) for c in destination.lower())


class MockWeatherProvider(WeatherProvider):
    """Returns synthetic but plausible weather + seasonal climatology."""

    async def get_forecast(self, destination: str) -> WeatherForecast:
        seed = _seed(destination)
        annual_mean = 5 + (seed % 25)  # 5..29 °C
        condition = _CONDITIONS[seed % len(_CONDITIONS)]
        logger.info(
            "weather.mock_forecast", destination=destination, mean=annual_mean
        )

        seasonal = [
            SeasonOutlook(
                season=name,
                avg_high_c=float(annual_mean + offset + 5),
                avg_low_c=float(annual_mean + offset - 5),
                note=note,
            )
            for name, offset, note in _SEASONS
        ]

        return WeatherForecast(
            destination=destination,
            condition=condition,
            temp_high_c=float(annual_mean + 7),
            temp_low_c=float(annual_mean - 3),
            humidity_pct=40 + (seed % 50),
            precipitation_chance_pct=(seed * 7) % 100,
            wind_kph=float(5 + (seed % 30)),
            seasonal_outlook=seasonal,
        )
