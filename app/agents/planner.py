"""Planner Agent.

The first agent in the pipeline: it turns a free-text travel request into the
structured `TripParameters` brief that downstream agents consume.

Implementation uses LangChain **structured output** — `model.with_structured_
output(TripParameters)` binds the Pydantic schema to the model (via tool/
function calling or JSON mode, depending on provider) so the model is forced to
return data that validates against the schema. No manual parsing required.

    chain = prompt | model.with_structured_output(TripParameters)

`PlannerAgent` wraps that chain, normalising failures into our application
error type. The chain builder takes the model as an argument so the agent is
testable with a stub, and `build_planner_agent_from_settings` wires the real
configured provider.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from langchain_core.runnables import Runnable

from app.agents.prompts.planner import build_planner_prompt
from app.core.config import Settings
from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger
from app.core.observability import traceable
from app.infrastructure.llm.factory import build_chat_model
from app.schemas.trip import TripParameters

if TYPE_CHECKING:
    from langchain_core.language_models.chat_models import BaseChatModel

logger = get_logger(__name__)


def build_planner_chain(model: BaseChatModel) -> Runnable:
    """Compose `prompt | structured-output model` into a single Runnable."""
    structured_model = model.with_structured_output(TripParameters)
    return build_planner_prompt() | structured_model


class PlannerAgent:
    """Extracts structured `TripParameters` from a natural-language request."""

    def __init__(self, chain: Runnable) -> None:
        self._chain = chain

    @traceable(run_type="chain", name="planner_agent")
    async def plan(self, user_request: str) -> TripParameters:
        logger.info("planner.extract", request_len=len(user_request))
        try:
            result = await self._chain.ainvoke({"request": user_request})
        except Exception as exc:  # provider/transport/validation failure
            logger.exception("planner.failed")
            raise ExternalServiceError(
                "The planner agent could not parse the request.",
                code="planner_failed",
            ) from exc

        # `with_structured_output` already returns a validated TripParameters.
        return result


def build_planner_agent_from_settings(settings: Settings) -> PlannerAgent:
    """Build the Planner Agent backed by the configured LLM provider."""
    return PlannerAgent(build_planner_chain(build_chat_model(settings)))
