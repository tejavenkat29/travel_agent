"""Transport comparison schemas (flight vs train vs bus)."""

from enum import Enum

from pydantic import BaseModel, Field


class TransportMode(str, Enum):
    FLIGHT = "flight"
    TRAIN = "train"
    BUS = "bus"


class FareClass(BaseModel):
    """A bookable fare class within a mode (e.g. train Sleeper / AC 3-Tier)."""

    name: str = Field(..., description="Class name, e.g. 'AC 3-Tier (3A)'")
    price_per_person: float = Field(..., description="Indicative fare per person")


class TransportOption(BaseModel):
    """A single transport mode's estimate (or why it's unavailable)."""

    mode: TransportMode
    available: bool = Field(..., description="Whether this mode is viable")
    provider: str | None = Field(default=None, description="Indicative operator")
    price_per_person: float | None = None
    total_price: float | None = None
    currency: str = "INR"
    duration_hours: float | None = None
    fare_classes: list[FareClass] = Field(
        default_factory=list,
        description="Per-class fares (e.g. Sleeper/3A/2A; Non-AC/AC Seater)",
    )
    booking_apps: list[str] = Field(
        default_factory=list, description="Where to book this mode"
    )
    note: str | None = Field(default=None, description="Feasibility note, if any")


class TransportComparison(BaseModel):
    """Multi-modal comparison with a recommended option (agent output)."""

    origin: str
    destination: str
    travelers: int
    currency: str
    options: list[TransportOption]
    recommended: TransportOption | None = None
    advisory: str = Field(..., description="Plain-language guidance / validation")
    disclaimer: str = Field(..., description="Data-source honesty note")
