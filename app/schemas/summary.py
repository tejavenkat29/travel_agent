"""Final summary schemas.

Composes the other agents' outputs into one structured `TravelSummary` plus a
`FinalResponse` that carries both the JSON and a rendered natural-language
Markdown summary.

`ItineraryPlan` is the LLM structured-output target (the only LLM-generated
part: recommendations + day-by-day plan). Everything else reuses the existing
agent schemas (`FlightOffer`, `WeatherAdvisory`, `BudgetEstimate`) so there is a
single source of truth and no data drift.
"""

from pydantic import BaseModel, Field

from app.schemas.budget import BudgetEstimate
from app.schemas.hotel import HotelInfo
from app.schemas.transport import TransportComparison
from app.schemas.trip import TripParameters
from app.schemas.weather import WeatherAdvisory

__all__ = [
    "HotelInfo",
    "DayPlan",
    "ItineraryPlan",
    "TravelSummary",
    "FinalResponseRequest",
    "FinalResponse",
]


class DayPlan(BaseModel):
    """A single day of the itinerary."""

    day: int = Field(..., ge=1, description="Day number")
    title: str = Field(..., description="Short theme for the day")
    activities: list[str] = Field(..., description="Concrete activities for the day")


class ItineraryPlan(BaseModel):
    """LLM-generated recommendations + daily itinerary."""

    recommendations: list[str] = Field(
        ..., description="Practical tips (food, transport, safety, local advice)"
    )
    daily_itinerary: list[DayPlan] = Field(
        ..., description="Day-by-day plan, one entry per trip day"
    )


class TravelSummary(BaseModel):
    """The full structured trip summary (machine-readable result)."""

    destination: str | None
    source: str | None
    travelers: int
    num_days: int
    currency: str
    transport: TransportComparison | None = Field(
        default=None, description="Flight/train/bus comparison + recommendation"
    )
    hotel: HotelInfo | None = None
    weather: WeatherAdvisory | None = None
    budget: BudgetEstimate | None = None
    recommendations: list[str] = Field(default_factory=list)
    daily_itinerary: list[DayPlan] = Field(default_factory=list)


class FinalResponseRequest(BaseModel):
    """Input: the collected outputs from all upstream agents."""

    trip: TripParameters
    transport: TransportComparison | None = Field(
        default=None, description="Comparison from the Transport Agent"
    )
    hotel: HotelInfo | None = None
    weather: WeatherAdvisory | None = None
    budget: BudgetEstimate | None = None


class FinalResponse(BaseModel):
    """Output: structured JSON + a rendered natural-language summary."""

    summary: TravelSummary = Field(..., description="Structured trip summary")
    natural_language: str = Field(
        ..., description="Human-friendly Markdown travel summary"
    )


class TripPlanRequest(BaseModel):
    """Input for the end-to-end `/plan` workflow.

    Supplying `provided_hotel` tells the workflow the user already booked a
    hotel, so that agent is skipped. `include_weather=False` skips weather.
    """

    request: str = Field(
        ..., min_length=3, description="Natural-language travel request"
    )
    provided_hotel: HotelInfo | None = Field(
        default=None, description="A hotel the user already booked (skips hotel search)"
    )
    include_weather: bool = Field(
        default=True, description="Set False to skip the weather agent"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "request": "Plan a 3 day trip from Mumbai to Tokyo for 2, "
                "budget $4000.",
                "include_weather": True,
            }
        }
    }
