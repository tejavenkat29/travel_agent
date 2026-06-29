"""LangGraph shared state.

`TravelState` is the single data structure that flows through the graph. Each
node receives the current state and returns a *partial* update; LangGraph merges
that update into the state (default channel behaviour = overwrite the key) and
passes the result to the next node. Think of it as the shared "trip folder" that
every agent reads from and adds to.

`total=False` means every field is optional — the state starts with only the
input fields and gets progressively filled in as nodes run.

The skip decisions read directly from this state:
- `hotel` already present     → the user booked a hotel    → skip the hotel node.
- `include_weather` is False  → the user disabled weather   → skip the weather node.
"""

from __future__ import annotations

from typing import TypedDict

from app.schemas.budget import BudgetEstimate
from app.schemas.hotel import HotelInfo
from app.schemas.summary import FinalResponse
from app.schemas.transport import TransportComparison
from app.schemas.trip import TripParameters
from app.schemas.weather import WeatherAdvisory

# Node names as constants (shared by the workflow and the router) so the edge
# wiring and routing logic can never drift apart.
# NOTE: a LangGraph node name must NOT equal a state-channel key, so the agent
# nodes are suffixed `_agent` (the channels are `transport`/`hotel`/`weather`/...).
PLANNER = "planner_agent"
TRANSPORT = "transport_agent"
HOTEL = "hotel_agent"
WEATHER = "weather_agent"
BUDGET = "budget_agent"
FINAL = "final_response_agent"


class TravelState(TypedDict, total=False):
    """State channels shared across all nodes."""

    user_request: str  # input: the raw natural-language request
    include_weather: bool  # input: user toggle (default treated as True)
    trip: TripParameters  # produced by the planner node
    transport: TransportComparison  # flight/train/bus comparison
    hotel: HotelInfo | None  # from the hotel node OR supplied by the user
    weather: WeatherAdvisory  # produced by the weather node
    budget: BudgetEstimate  # produced by the budget node
    final: FinalResponse  # produced by the final-response node
