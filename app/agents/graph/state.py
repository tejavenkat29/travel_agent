"""LangGraph shared state.

`TravelState` is the single data structure that flows through the graph. Each
node receives the current state and returns a *partial* update; LangGraph merges
that update into the state (default channel behaviour = overwrite the key) and
passes the result to the next node. Think of it as the shared "trip folder" that
every agent reads from and adds to.

`total=False` means every field is optional — the state starts with just
`user_request` and gets progressively filled in as nodes run.
"""

from __future__ import annotations

from typing import TypedDict

from app.schemas.budget import BudgetEstimate
from app.schemas.flight import FlightOffer
from app.schemas.summary import FinalResponse, HotelInfo
from app.schemas.trip import TripParameters
from app.schemas.weather import WeatherAdvisory


class TravelState(TypedDict, total=False):
    """State channels shared across all nodes."""

    user_request: str  # input: the raw natural-language request
    trip: TripParameters  # produced by the planner node
    flights: list[FlightOffer]  # produced by the flight node
    weather: WeatherAdvisory  # produced by the weather node
    hotel: HotelInfo | None  # reserved for a future hotel node
    budget: BudgetEstimate  # produced by the budget node
    final: FinalResponse  # produced by the final-response node
