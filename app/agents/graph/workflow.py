"""LangGraph workflow definition.

Wires the nodes into a directed graph and compiles it into a runnable.

LangGraph concepts used here:
- `StateGraph(TravelState)` — a graph whose every node shares the `TravelState`
  schema. It declares the channels (state keys) and how nodes connect.
- `add_node(name, fn)` — registers a node (our agent adapters).
- `add_edge(a, b)` — an unconditional transition: after `a` finishes, run `b`.
- `START` / `END` — the built-in virtual entry and exit nodes. `START -> first`
  marks where execution begins; `last -> END` marks where it stops.
- `.compile()` — validates the graph and returns a runnable (a Pebble/Runnable)
  exposing `.invoke()` / `.ainvoke()`.

This is a simple linear pipeline (no conditional routing yet):

    START → planner → flights → weather → budget → final_response → END
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.agents.graph.nodes import TravelNodes
from app.agents.graph.state import TravelState
from app.core.config import Settings


def build_travel_workflow(nodes: TravelNodes) -> CompiledStateGraph:
    """Assemble and compile the linear travel-planning graph."""
    graph = StateGraph(TravelState)

    # --- Nodes ---
    graph.add_node("planner", nodes.planner_node)
    graph.add_node("flights", nodes.flight_node)
    graph.add_node("weather", nodes.weather_node)
    graph.add_node("budget", nodes.budget_node)
    graph.add_node("final_response", nodes.final_node)

    # --- Edges (linear, unconditional) ---
    graph.add_edge(START, "planner")
    graph.add_edge("planner", "flights")
    graph.add_edge("flights", "weather")
    graph.add_edge("weather", "budget")
    graph.add_edge("budget", "final_response")
    graph.add_edge("final_response", END)

    return graph.compile()


def build_travel_workflow_from_settings(settings: Settings) -> CompiledStateGraph:
    """Build the workflow with agents wired to the configured providers."""
    from app.agents.budget import build_budget_agent_from_settings
    from app.agents.final_response import (
        build_final_response_agent_from_settings,
    )
    from app.agents.flight import build_flight_agent_from_settings
    from app.agents.planner import build_planner_agent_from_settings
    from app.agents.weather import build_weather_agent_from_settings

    nodes = TravelNodes(
        planner=build_planner_agent_from_settings(settings),
        flight=build_flight_agent_from_settings(settings),
        weather=build_weather_agent_from_settings(settings),
        budget=build_budget_agent_from_settings(settings),
        final=build_final_response_agent_from_settings(settings),
    )
    return build_travel_workflow(nodes)
