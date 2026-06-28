"""LLM service port (interface).

Defines the *contract* the application depends on for talking to a language
model, with zero reference to OpenAI/Gemini/Ollama or LangChain. Use cases and
routes depend on this abstraction; the concrete implementation lives in the
infrastructure layer and is injected at runtime. This is the dependency-
inversion boundary that makes the provider swappable.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.chat import ChatResult, Message


class AbstractLLMService(ABC):
    """Provider-agnostic chat interface."""

    @abstractmethod
    async def chat(
        self,
        messages: list[Message],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> ChatResult:
        """Send a conversation to the model and return its reply."""
        raise NotImplementedError
