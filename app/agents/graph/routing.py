"""Conditional routing for the workflow.

`route_after_planner` is the path function used by LangGraph's conditional
edges. After the planner runs, it inspects the state and returns the **list of
nodes to execute next** — LangGraph dispatches all of them in parallel, so
returning a subset is how we *skip* agents.

Decisions:
- Transport always runs (we always compare flight/train/bus).
- Skip `hotel` when the state already has a hotel (the user already booked).
- Skip `weather` when `include_weather` is False (the user disabled it).

Returning a list makes this a dynamic fan-out.
"""

from __future__ import annotations

from app.agents.graph.state import (
    HOTEL,
    TRANSPORT,
    WEATHER,
    TravelState,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


def route_after_planner(state: TravelState) -> list[str]:
    """Return the subset of {transport, hotel, weather} to run next."""
    targets: list[str] = [TRANSPORT]  # transport is always evaluated

    if state.get("hotel"):
        logger.info("route.skip", agent=HOTEL, reason="user_booked_hotel")
    else:
        targets.append(HOTEL)

    if state.get("include_weather", True):
        targets.append(WEATHER)
    else:
        logger.info("route.skip", agent=WEATHER, reason="weather_disabled")

    logger.info("route.after_planner", targets=targets)
    return targets
