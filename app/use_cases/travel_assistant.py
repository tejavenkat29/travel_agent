"""Travel-assistant use case (application layer).

Orchestrates one user goal — "recommend a destination" — by mapping the request
into the chain's input variables, invoking the chain, and normalising failures
into our application error type. It depends only on a `Runnable` (the chain),
not on any provider, so it stays framework-agnostic and easily testable.
"""

from __future__ import annotations

from langchain_core.runnables import Runnable

from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger
from app.schemas.travel import TravelRecommendation

logger = get_logger(__name__)


class TravelAssistantUseCase:
    """Produce a structured travel recommendation from a free-text request."""

    def __init__(self, chain: Runnable) -> None:
        self._chain = chain

    async def recommend(
        self, *, query: str, duration_days: int, budget_usd: float | None
    ) -> TravelRecommendation:
        budget = f"${budget_usd:,.0f}" if budget_usd else "flexible"
        try:
            result = await self._chain.ainvoke(
                {
                    "query": query,
                    "duration_days": duration_days,
                    "budget": budget,
                }
            )
        except Exception as exc:  # LLM transport or output-parsing failure
            logger.exception("travel_assistant.failed")
            raise ExternalServiceError(
                "The travel assistant could not produce a recommendation.",
                code="travel_assistant_failed",
            ) from exc

        return result
