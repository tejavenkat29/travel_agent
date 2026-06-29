"""LangGraph travel-planning workflow (with conditional routing).

Connects all agents into one compiled graph. After the planner extracts the
trip, a **conditional edge** decides which of the Flight, Hotel and Weather
agents to run — they fan out in parallel, then the Budget agent joins their
results, and the Final Response agent synthesizes everything.

    START
      │
    planner                         (extract TripParameters)
      │  ◇ conditional edge: route_after_planner(state) -> [subset]
      ├──────────┬──────────┐       fan-out: only the NON-skipped agents
   flights     hotel     weather    (each writes a different state channel)
      │          │          │
      └──────────┴──────────┘       fan-in / join
      │
    budget                          (runs after the dispatched agents finish)
      │
   final_response                   (synthesize JSON + natural language)
      │
     END

Why a conditional edge (vs. gating inside each node):
- The skip is a *routing* decision, so it belongs on the edge. Skipped nodes
  never execute at all — no wasted LLM/provider calls, and the graph diagram
  honestly reflects what ran.
- Returning a LIST from the router gives a dynamic fan-out: we run exactly the
  subset we need, and the static `*->budget` edges still form the join.
- If all optional agents are skipped, the router targets `budget` directly so
  the graph always reaches the join and END.

State transitions: the planner writes `trip`; the dispatched subset of
{flights, hotel, weather} run concurrently (each writing a different channel, so
the default overwrite reducer merges them conflict-free); `budget` joins and
reads the merged flights/hotel; `final_response` reads everything and writes
`final`. Pre-supplied flight/hotel are seeded into the initial state, so even
when their agents are skipped their data still flows to budget and final.
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.agents.graph.nodes import TravelNodes
from app.agents.graph.routing import route_after_planner
from app.agents.graph.state import (
    BUDGET,
    FINAL,
    HOTEL,
    PLANNER,
    TRANSPORT,
    WEATHER,
    TravelState,
)
from app.core.config import Settings

# The agents that may fan out in parallel after the planner.
_PARALLEL_NODES = (TRANSPORT, HOTEL, WEATHER)


def build_travel_workflow(nodes: TravelNodes) -> CompiledStateGraph:
    """Assemble and compile the conditional travel-planning graph."""
    graph = StateGraph(TravelState)

    # --- Register nodes ---
    graph.add_node(PLANNER, nodes.planner_node)
    graph.add_node(TRANSPORT, nodes.transport_node)
    graph.add_node(HOTEL, nodes.hotel_node)
    graph.add_node(WEATHER, nodes.weather_node)
    graph.add_node(BUDGET, nodes.budget_node)
    graph.add_node(FINAL, nodes.final_node)

    # --- Entry ---
    graph.add_edge(START, PLANNER)

    # --- Conditional fan-out: planner -> dynamic subset of parallel agents ---
    # `route_after_planner` returns a list of node names to run. The path map
    # (4th arg) declares every node the router could possibly target.
    graph.add_conditional_edges(
        PLANNER,
        route_after_planner,
        [*_PARALLEL_NODES, BUDGET],
    )

    # --- Fan-in: {transport, hotel, weather} -> budget (join) ---
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
    from app.agents.hotel import build_hotel_agent_from_settings
    from app.agents.planner import build_planner_agent_from_settings
    from app.agents.transport import build_transport_agent_from_settings
    from app.agents.weather import build_weather_agent_from_settings

    nodes = TravelNodes(
        planner=build_planner_agent_from_settings(settings),
        transport=build_transport_agent_from_settings(settings),
        hotel=build_hotel_agent_from_settings(settings),
        weather=build_weather_agent_from_settings(settings),
        budget=build_budget_agent_from_settings(settings),
        final=build_final_response_agent_from_settings(settings),
    )
    return build_travel_workflow(nodes)
