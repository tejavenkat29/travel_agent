"""Weather schemas — provider data vs. agent advice.

`WeatherForecast` is the raw, provider-agnostic data every weather provider must
return (mock or a real API). `WeatherAdvisory` is what the Weather *Agent*
produces: the forecast plus derived guidance (clothing + best time to visit).
Keeping these separate enforces the single-responsibility split — providers
report facts, the agent interprets them.
"""

from pydantic import BaseModel, Field


class SeasonOutlook(BaseModel):
    """Climatology summary for one season (used to pick the best visit time)."""

    season: str = Field(..., description="Spring / Summer / Autumn / Winter")
    avg_high_c: float = Field(..., description="Average daytime high (°C)")
    avg_low_c: float = Field(..., description="Average nighttime low (°C)")
    note: str = Field(..., description="Short seasonal note")


class WeatherForecast(BaseModel):
    """Raw weather data returned by a provider (no interpretation)."""

    destination: str = Field(..., description="Location the forecast is for")
    condition: str = Field(..., description="Headline condition, e.g. 'Sunny'")
    temp_high_c: float = Field(..., description="Expected daytime high (°C)")
    temp_low_c: float = Field(..., description="Expected nighttime low (°C)")
    humidity_pct: int = Field(..., ge=0, le=100, description="Relative humidity")
    precipitation_chance_pct: int = Field(
        ..., ge=0, le=100, description="Chance of precipitation"
    )
    wind_kph: float = Field(..., ge=0, description="Wind speed (km/h)")
    seasonal_outlook: list[SeasonOutlook] = Field(
        ..., description="Per-season climatology for visit-time advice"
    )


class WeatherRequest(BaseModel):
    """Input for the weather endpoint."""

    destination: str = Field(
        ..., min_length=2, description="Destination city/country"
    )

    model_config = {"json_schema_extra": {"example": {"destination": "Tokyo"}}}


class WeatherAdvisory(BaseModel):
    """Weather Agent output — forecast plus derived guidance."""

    forecast: WeatherForecast
    clothing_suggestions: list[str] = Field(
        ..., description="What to pack/wear for the expected conditions"
    )
    best_seasons: list[str] = Field(
        ..., description="Season(s) with the most comfortable weather"
    )
    best_time_to_visit: str = Field(
        ..., description="Human-readable best-time-to-visit recommendation"
    )
