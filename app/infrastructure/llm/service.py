"""LangChain-backed LLM service — the reusable implementation.

`LangChainLLMService` implements the domain `AbstractLLMService` port on top of
any LangChain `BaseChatModel`, so the same code path serves OpenAI, Gemini and
Ollama. It translates domain `Message`s to LangChain messages, invokes the
model asynchronously, and wraps provider failures in our `ExternalServiceError`
so callers never see raw SDK exceptions.

`build_llm_service(settings)` is the assembly helper used by dependency
injection to produce a ready-to-use service for the configured provider.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.core.config import Settings
from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger
from app.domain.entities.chat import ChatResult, Message, Role
from app.domain.interfaces.llm import AbstractLLMService
from app.infrastructure.llm.factory import build_chat_model, resolve_model_name

if TYPE_CHECKING:
    from langchain_core.language_models.chat_models import BaseChatModel

logger = get_logger(__name__)


def _to_langchain_messages(messages: list[Message]) -> list:
    """Map domain messages to LangChain message objects (lazy import)."""
    from langchain_core.messages import (
        AIMessage,
        HumanMessage,
        SystemMessage,
    )

    mapping = {
        Role.SYSTEM: SystemMessage,
        Role.USER: HumanMessage,
        Role.ASSISTANT: AIMessage,
    }
    return [mapping[m.role](content=m.content) for m in messages]


class LangChainLLMService(AbstractLLMService):
    """Provider-agnostic chat service wrapping a LangChain chat model."""

    def __init__(
        self, model: BaseChatModel, *, provider: str, model_name: str
    ) -> None:
        self._model = model
        self._provider = provider
        self._model_name = model_name

    async def chat(
        self,
        messages: list[Message],
        *,
        temperature: float | None = None,  # noqa: ARG002 (per-call override TODO)
        max_tokens: int | None = None,  # noqa: ARG002
    ) -> ChatResult:
        lc_messages = _to_langchain_messages(messages)
        try:
            response = await self._model.ainvoke(lc_messages)
        except Exception as exc:  # normalise any SDK/transport failure
            logger.exception("llm.invoke_failed", provider=self._provider)
            raise ExternalServiceError(
                f"The LLM provider '{self._provider}' failed to respond.",
                code="llm_request_failed",
            ) from exc

        content = response.content if isinstance(response.content, str) else str(
            response.content
        )
        return ChatResult(
            content=content, provider=self._provider, model=self._model_name
        )


def build_llm_service(settings: Settings) -> LangChainLLMService:
    """Assemble a ready-to-use LLM service for the configured provider."""
    model = build_chat_model(settings)
    return LangChainLLMService(
        model,
        provider=settings.LLM_PROVIDER.value,
        model_name=resolve_model_name(settings),
    )
