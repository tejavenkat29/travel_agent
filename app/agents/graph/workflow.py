"""LangGraph travel-planning workflow.

Connects all agents into one compiled graph. The topology is a **fan-out /
fan-in** (not a straight line): after the planner extracts the trip, the
Flight, Hotel and Weather agents run **in parallel**, then the Budget agent
joins their results, and the Final Response agent synthesizes everything.

    START
      │
    planner                         (extract TripParameters)
      │
      ├──────────┬──────────┐       fan-out: run concurrently
   flights     hotel     weather    (each writes a different state channel)
      │          │          │
      └──────────┴──────────┘       fan-in / join
      │
    budget                          (needs flights + hotel; reads the joined state)
      │
   final_response                   (synthesize JSON + natural language)
      │
     END

State transitions (LangGraph executes in "supersteps" — batches of nodes that
run together, then their updates are merged into the state before the next
batch):

  • Superstep 1 — `planner` runs, writes `trip`.
  • Superstep 2 — `flights`, `hotel`, `weather` run concurrently. Each returns a
    partial update for a DIFFERENT channel (`flights`, `hotel`, `weather`), so
    the default "overwrite" reducer merges them with no conflict. (If two
    parallel nodes wrote the same channel, a custom reducer would be required.)
  • Superstep 3 — `budget` runs only after ALL three predecessors complete
    (the three incoming edges form the join), so the merged `flights`/`hotel`
    are available; it writes `budget`.
  • Superstep 4 — `final_response` runs, reads the whole accumulated state,
    writes `final`. Then END.

No conditional routing: every edge is unconditional.
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.agents.graph.nodes import TravelNodes
from app.agents.graph.state import TravelState
from app.core.config import Settings

# Node names (kept as constants to avoid stringly-typed edge wiring drift).
PLANNER = "planner"
FLIGHTS = "flights"
HOTEL = "hotel"
WEATHER = "weather"
BUDGET = "budget"
FINAL = "final_response"

# The agents that fan out in parallel after the planner.
_PARALLEL_NODES = (FLIGHTS, HOTEL, WEATHER)


def build_travel_workflow(nodes: TravelNodes) -> CompiledStateGraph:
    """Assemble and compile the parallel travel-planning graph."""
    graph = StateGraph(TravelState)

    # --- Register nodes ---
    graph.add_node(PLANNER, nodes.planner_node)
    graph.add_node(FLIGHTS, nodes.flight_node)
    graph.add_node(HOTEL, nodes.hotel_node)
    graph.add_node(WEATHER, nodes.weather_node)
    graph.add_node(BUDGET, nodes.budget_node)
    graph.add_node(FINAL, nodes.final_node)

    # --- Entry ---
    graph.add_edge(START, PLANNER)

    # --- Fan-out: planner -> {flights, hotel, weather} (run in parallel) ---
    for node in _PARALLEL_NODES:
        graph.add_edge(PLANNER, node)

    # --- Fan-in: {flights, hotel, weather} -> budget (join) ---
    for node in _PARALLEL_NODES:
        graph.add_edge(node, BUDGET)

    # --- Tail ---
    graph.add_edge(BUDGET, FINAL)
    graph.add_edge(FINAL, END)

    return graph.compile()


def build_travel_workflow_from_settings(settings: Settings) -> CompiledStateGraph:
    """Build the workflow with agents wired to the configured providers."""
    from app.agents.budget import build_budget_agent_from_settings
    from app.agents.final_response import (
        build_final_response_agent_from_settings,
    )
    from app.agents.flight import build_flight_agent_from_settings
    from app.agents.hotel import build_hotel_agent_from_settings
    from app.agents.planner import build_planner_agent_from_settings
    from app.agents.weather import build_weather_agent_from_settings

    nodes = TravelNodes(
        planner=build_planner_agent_from_settings(settings),
        flight=build_flight_agent_from_settings(settings),
        hotel=build_hotel_agent_from_settings(settings),
        weather=build_weather_agent_from_settings(settings),
        budget=build_budget_agent_from_settings(settings),
        final=build_final_response_agent_from_settings(settings),
    )
    return build_travel_workflow(nodes)
