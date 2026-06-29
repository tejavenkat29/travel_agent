"""Hotel schemas — search criteria, offers, selected hotel, response.

`HotelOffer` is the provider-agnostic result shape (mock or real API).
`HotelInfo` is the *selected* hotel with trip-specific totals (nights x rate),
shared with the summary layer. Keeping `HotelInfo` here makes the hotel package
the single source of truth for hotel data.
"""

from pydantic import BaseModel, Field


class HotelSearchCriteria(BaseModel):
    """Normalised, provider-agnostic hotel query."""

    destination: str = Field(..., description="City/area to search")
    nights: int = Field(..., ge=1, description="Number of nights")
    guests: int = Field(default=1, ge=1, description="Number of guests")
    currency: str = Field(default="USD", description="Preferred currency")


class HotelOffer(BaseModel):
    """A single hotel option (shape shared by all providers)."""

    name: str = Field(..., description="Hotel name")
    area: str = Field(..., description="Neighbourhood/area")
    rating: float = Field(..., ge=0, le=5, description="Star rating")
    nightly_rate: float = Field(..., ge=0, description="Cost per night")
    currency: str = Field(..., description="Currency")
    amenities: list[str] = Field(default_factory=list, description="Key amenities")


class HotelInfo(BaseModel):
    """The selected hotel, with trip-specific totals."""

    name: str = Field(..., description="Hotel name")
    area: str | None = Field(default=None, description="Neighbourhood/area")
    rating: float | None = Field(default=None, ge=0, le=5, description="Star rating")
    nightly_rate: float = Field(..., ge=0, description="Cost per night")
    nights: int = Field(..., ge=1, description="Number of nights")
    total_price: float = Field(..., ge=0, description="Total room cost")
    currency: str = Field(default="USD", description="Currency")


class HotelSearchResponse(BaseModel):
    """Response body for the hotel-search endpoint."""

    destination: str
    nights: int
    currency: str
    count: int = Field(..., description="Number of offers returned")
    selected: HotelInfo | None = Field(
        default=None, description="The agent's recommended hotel"
    )
    offers: list[HotelOffer] = Field(..., description="Offers, best-rated first")
