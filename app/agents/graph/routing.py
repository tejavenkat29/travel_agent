"""Conditional routing for the workflow.

`route_after_planner` is the path function used by LangGraph's conditional
edges. After the planner runs, it inspects the state and returns the **list of
nodes to execute next** — LangGraph dispatches all of them in parallel, so
returning a subset is how we *skip* agents.

Decisions (each maps to one requirement):
- Skip `flights` when the state already has flights (the user supplied one).
- Skip `hotel` when the state already has a hotel (the user already booked).
- Skip `weather` when `include_weather` is False (the user disabled it).

Returning a list (not a single string) makes this a dynamic fan-out. If every
optional agent is skipped, we route straight to `budget` so the graph still
reaches the join and finishes (a router must always return at least one target).
"""

from __future__ import annotations

from app.agents.graph.state import (
    BUDGET,
    FLIGHTS,
    HOTEL,
    WEATHER,
    TravelState,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


def route_after_planner(state: TravelState) -> list[str]:
    """Return the subset of {flights, hotel, weather} to run next."""
    targets: list[str] = []

    if state.get("flights"):
        logger.info("route.skip", agent=FLIGHTS, reason="user_supplied_flight")
    else:
        targets.append(FLIGHTS)

    if state.get("hotel"):
        logger.info("route.skip", agent=HOTEL, reason="user_booked_hotel")
    else:
        targets.append(HOTEL)

    if state.get("include_weather", True):
        targets.append(WEATHER)
    else:
        logger.info("route.skip", agent=WEATHER, reason="weather_disabled")

    # A router must return at least one node; if everything is skipped, go
    # straight to the join so the graph still completes.
    resolved = targets or [BUDGET]
    logger.info("route.after_planner", targets=resolved)
    return resolved
