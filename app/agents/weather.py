"""Weather Agent.

Receives a destination, fetches raw weather from the injected `WeatherProvider`,
and *interprets* it into actionable advice: what to wear and when to visit.

Responsibility split (SRP): the provider reports facts; this agent turns facts
into recommendations. The clothing and best-time rules are pure functions of the
forecast, so they are deterministic and unit-testable in isolation.
"""

from __future__ import annotations

from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger
from app.core.observability import traceable
from app.domain.interfaces.weather import WeatherProvider
from app.schemas.weather import SeasonOutlook, WeatherAdvisory, WeatherForecast

logger = get_logger(__name__)

# Comfortable mean-temperature band (°C) used to rank seasons.
_COMFORT_LOW = 15.0
_COMFORT_HIGH = 27.0


def _suggest_clothing(forecast: WeatherForecast) -> list[str]:
    """Derive packing/clothing advice from raw conditions."""
    tips: list[str] = []
    high, low = forecast.temp_high_c, forecast.temp_low_c

    if high >= 30:
        tips.append("Light, breathable clothing (cotton/linen)")
        tips.append("Sun protection: hat, sunglasses, sunscreen")
    elif high >= 20:
        tips.append("Comfortable daytime wear; a light layer for evenings")
    elif high >= 10:
        tips.append("A warm jacket or sweater")
    else:
        tips.append("Heavy winter coat and warm layers")

    if low <= 5:
        tips.append("Thermal layers, gloves and a scarf for cold nights")
    if forecast.precipitation_chance_pct >= 40:
        tips.append("Umbrella or waterproof jacket — rain likely")
    if forecast.wind_kph >= 25:
        tips.append("A windproof outer layer")
    if forecast.humidity_pct >= 70 and high >= 25:
        tips.append("Moisture-wicking fabrics for humidity")

    return tips


def _best_seasons(outlook: list[SeasonOutlook]) -> list[SeasonOutlook]:
    """Pick the season(s) whose mean temperature is most comfortable."""

    def mean(s: SeasonOutlook) -> float:
        return (s.avg_high_c + s.avg_low_c) / 2

    comfortable = [s for s in outlook if _COMFORT_LOW <= mean(s) <= _COMFORT_HIGH]
    if comfortable:
        return comfortable
    # Otherwise, the single season closest to the comfort midpoint.
    midpoint = (_COMFORT_LOW + _COMFORT_HIGH) / 2
    return [min(outlook, key=lambda s: abs(mean(s) - midpoint))]


class WeatherAgent:
    """Turns a destination into weather + clothing + best-time advice."""

    def __init__(self, provider: WeatherProvider) -> None:
        self._provider = provider

    @traceable(run_type="chain", name="weather_agent")
    async def advise(self, destination: str) -> WeatherAdvisory:
        try:
            forecast = await self._provider.get_forecast(destination)
        except ExternalServiceError:
            raise
        except Exception as exc:  # normalise unexpected provider failures
            logger.exception("weather.forecast_failed")
            raise ExternalServiceError(
                "The weather provider failed to return a forecast.",
                code="weather_forecast_failed",
            ) from exc

        clothing = _suggest_clothing(forecast)
        best = _best_seasons(forecast.seasonal_outlook)
        best_names = [s.season for s in best]
        best_sentence = (
            f"The best time to visit {destination} is "
            f"{' or '.join(best_names)} — "
            f"{best[0].note.lower()}."
        )

        logger.info("weather.advised", destination=destination, best=best_names)
        return WeatherAdvisory(
            forecast=forecast,
            clothing_suggestions=clothing,
            best_seasons=best_names,
            best_time_to_visit=best_sentence,
        )


def build_weather_agent_from_settings(settings) -> WeatherAgent:
    """Build the Weather Agent with the configured provider."""
    from app.infrastructure.external.weather.factory import build_weather_provider

    return WeatherAgent(build_weather_provider(settings))
