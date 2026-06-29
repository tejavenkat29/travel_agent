"""LangFlow component: Planner Agent.

A thin LangFlow wrapper around the same `PlannerAgent` used by the LangGraph
workflow — proving the agents are reusable across orchestrators. Drop this file
into LangFlow's components directory (LANGFLOW_COMPONENTS_PATH) with the project
on PYTHONPATH so `app` is importable.
"""

from __future__ import annotations

import asyncio

from langflow.custom import Component
from langflow.io import MessageTextInput, Output
from langflow.schema import Data


class PlannerAgentComponent(Component):
    display_name = "Planner Agent"
    description = "Extract structured trip parameters from a free-text request."
    icon = "map-pin"
    name = "PlannerAgent"

    inputs = [
        MessageTextInput(
            name="request",
            display_name="User Request",
            info="Natural-language travel request",
        )
    ]
    outputs = [Output(display_name="Trip", name="trip", method="run_planner")]

    def run_planner(self) -> Data:
        from app.agents.planner import build_planner_agent_from_settings
        from app.core.config import settings

        agent = build_planner_agent_from_settings(settings)
        trip = asyncio.run(agent.plan(self.request))
        self.status = trip.model_dump()
        return Data(data=trip.model_dump())
