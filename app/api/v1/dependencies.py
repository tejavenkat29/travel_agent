"""FastAPI dependency-injection wiring.

Central place to declare reusable `Depends(...)` providers (DB sessions, Redis
client, LLM provider, current settings, authenticated user, ...). Concrete
providers are added as the infrastructure layer is implemented.
"""

from functools import lru_cache
from typing import TYPE_CHECKING

from app.core.config import Settings, get_settings
from app.domain.interfaces.llm import AbstractLLMService

if TYPE_CHECKING:
    from app.agents.planner import PlannerAgent
    from app.use_cases.travel_assistant import TravelAssistantUseCase


def get_app_settings() -> Settings:
    """Expose validated settings to route handlers via DI."""
    return get_settings()


@lru_cache
def get_llm_service() -> AbstractLLMService:
    """Provide a process-wide singleton LLM service for the active provider.

    Cached so the chat model (and its underlying HTTP client) is built once and
    reused across requests. Routes depend on the `AbstractLLMService` port, not
    the concrete implementation, keeping the provider swappable.
    """
    # Imported lazily so the app and tests can load without provider SDKs.
    from app.infrastructure.llm.service import build_llm_service

    return build_llm_service(get_settings())


@lru_cache
def get_travel_assistant() -> "TravelAssistantUseCase":
    """Provide a cached travel-assistant use case backed by the LCEL chain."""
    from app.agents.chains.travel_chain import build_travel_chain_from_settings
    from app.use_cases.travel_assistant import TravelAssistantUseCase

    chain = build_travel_chain_from_settings(get_settings())
    return TravelAssistantUseCase(chain)


@lru_cache
def get_planner_agent() -> "PlannerAgent":
    """Provide a cached Planner Agent backed by the configured provider."""
    from app.agents.planner import build_planner_agent_from_settings

    return build_planner_agent_from_settings(get_settings())
