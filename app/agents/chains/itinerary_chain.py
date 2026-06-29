"""Itinerary chain (LCEL).

`prompt | model.with_structured_output(ItineraryPlan)` — produces a validated
`ItineraryPlan` (recommendations + daily itinerary). Takes the model as an
argument so it is testable with a stub.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from langchain_core.runnables import Runnable

from app.agents.prompts.itinerary import build_itinerary_prompt
from app.core.config import Settings
from app.infrastructure.llm.factory import build_chat_model
from app.schemas.summary import ItineraryPlan

if TYPE_CHECKING:
    from langchain_core.language_models.chat_models import BaseChatModel


def build_itinerary_chain(model: BaseChatModel) -> Runnable:
    """Compose the itinerary-generation chain."""
    return build_itinerary_prompt() | model.with_structured_output(ItineraryPlan)


def build_itinerary_chain_from_settings(settings: Settings) -> Runnable:
    """Build the itinerary chain backed by the configured provider."""
    return build_itinerary_chain(build_chat_model(settings))
