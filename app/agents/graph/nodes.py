"""LangGraph nodes.

A *node* is a unit of work in the graph: an (async) callable that takes the
current `TravelState` and returns a dict of state updates. Here each node is a
thin adapter that calls one existing agent and writes its result into the
shared state — so the agents themselves stay framework-agnostic and reusable
outside the graph.

The agents are injected into `TravelNodes`, keeping the nodes testable with
stubs and free of any provider/LLM construction logic.
"""

from __future__ import annotations

from app.agents.budget import BudgetAgent
from app.agents.final_response import FinalResponseAgent
from app.agents.flight import FlightAgent
from app.agents.hotel import HotelAgent
from app.agents.planner import PlannerAgent
from app.agents.weather import WeatherAgent
from app.agents.graph.state import TravelState
from app.core.logging import get_logger
from app.schemas.summary import FinalResponseRequest

logger = get_logger(__name__)


class TravelNodes:
    """Holds the agents and exposes one node method per agent."""

    def __init__(
        self,
        *,
        planner: PlannerAgent,
        flight: FlightAgent,
        hotel: HotelAgent,
        weather: WeatherAgent,
        budget: BudgetAgent,
        final: FinalResponseAgent,
    ) -> None:
        self._planner = planner
        self._flight = flight
        self._hotel = hotel
        self._weather = weather
        self._budget = budget
        self._final = final

    async def planner_node(self, state: TravelState) -> dict:
        """Extract structured trip parameters from the user request."""
        logger.info("node.planner")
        trip = await self._planner.plan(state["user_request"])
        return {"trip": trip}

    async def flight_node(self, state: TravelState) -> dict:
        """Find flight offers for the trip."""
        logger.info("node.flights")
        offers = await self._flight.find_flights(state["trip"])
        return {"flights": offers}

    async def hotel_node(self, state: TravelState) -> dict:
        """Find and recommend a hotel for the destination."""
        logger.info("node.hotel")
        if not state["trip"].destination:
            return {}  # nothing to look up without a destination
        hotel = await self._hotel.find_hotel(state["trip"])
        return {"hotel": hotel}

    async def weather_node(self, state: TravelState) -> dict:
        """Fetch weather + advice for the destination."""
        logger.info("node.weather")
        destination = state["trip"].destination
        if not destination:
            return {}  # nothing to look up without a destination
        advisory = await self._weather.advise(destination)
        return {"weather": advisory}

    async def budget_node(self, state: TravelState) -> dict:
        """Estimate cost using the actual cheapest flight + selected hotel rate.

        This node is the join point: it runs only after flights, hotel and
        weather have all completed, so their results are available in state.
        """
        logger.info("node.budget")
        offers = state.get("flights") or []
        flight_total = min((o.total_price for o in offers), default=None)
        hotel = state.get("hotel")
        hotel_per_night = hotel.nightly_rate if hotel else None
        estimate = await self._budget.estimate(
            state["trip"],
            flight_total=flight_total,
            hotel_per_night=hotel_per_night,
        )
        return {"budget": estimate}

    async def final_node(self, state: TravelState) -> dict:
        """Synthesize everything into the final summary."""
        logger.info("node.final_response")
        request = FinalResponseRequest(
            trip=state["trip"],
            flights=state.get("flights") or [],
            hotel=state.get("hotel"),
            weather=state.get("weather"),
            budget=state.get("budget"),
        )
        final = await self._final.compose(request)
        return {"final": final}
