"""Flight schemas — search criteria, offers, and the agent's response.

`FlightSearchCriteria` is the *normalised query* a provider understands (it is
intentionally decoupled from `TripParameters` so providers never depend on the
planner's shape). `FlightOffer` is the provider-agnostic result shape every
provider must return, so the mock and a future real API are interchangeable.
"""

from pydantic import BaseModel, Field


class FlightSearchCriteria(BaseModel):
    """Normalised, provider-agnostic flight query."""

    origin: str = Field(..., description="Departure city/airport")
    destination: str = Field(..., description="Arrival city/airport")
    passengers: int = Field(default=1, ge=1, description="Number of travelers")
    currency: str = Field(default="USD", description="Preferred fare currency")


class FlightOffer(BaseModel):
    """A single bookable flight option (shape shared by all providers)."""

    airline: str = Field(..., description="Operating airline")
    flight_number: str = Field(..., description="Flight identifier")
    origin: str = Field(..., description="Departure city/airport")
    destination: str = Field(..., description="Arrival city/airport")
    departure_time: str = Field(..., description="Local departure time (HH:MM)")
    arrival_time: str = Field(..., description="Local arrival time (HH:MM)")
    duration_minutes: int = Field(..., description="Total travel time in minutes")
    stops: int = Field(..., ge=0, description="Number of layovers")
    fare_per_person: float = Field(..., description="Price per traveler")
    total_price: float = Field(..., description="Price for all travelers")
    currency: str = Field(..., description="Fare currency")
    seats_available: int = Field(..., ge=0, description="Remaining seats")
    within_budget: bool | None = Field(
        default=None,
        description="Whether total_price fits the trip budget (set by the agent)",
    )


class FlightSearchResponse(BaseModel):
    """Response body for the flight-search endpoint."""

    origin: str
    destination: str
    passengers: int
    currency: str
    count: int = Field(..., description="Number of offers returned")
    offers: list[FlightOffer] = Field(..., description="Offers, cheapest first")
