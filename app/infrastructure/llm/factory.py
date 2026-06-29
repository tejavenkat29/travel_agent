"""LLM provider factory — centralised LLM configuration.

The single place that knows how to construct a concrete LangChain chat model
for each supported provider (OpenAI / Gemini / Ollama) from `Settings`. Adding
a new provider means editing only this file.

Provider SDKs are imported *lazily* inside each branch so the application can
boot (and the other providers can be used) even if a given SDK isn't installed.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.core.config import LLMProvider, Settings
from app.core.exceptions import ExternalServiceError
from app.core.logging import get_logger

if TYPE_CHECKING:  # imported only for type checking; no runtime dependency
    from langchain_core.language_models.chat_models import BaseChatModel

logger = get_logger(__name__)


def resolve_model_name(settings: Settings) -> str:
    """Return the configured model name for the active provider."""
    return {
        LLMProvider.OPENAI: settings.OPENAI_MODEL,
        LLMProvider.GEMINI: settings.GEMINI_MODEL,
        LLMProvider.OLLAMA: settings.OLLAMA_MODEL,
    }[settings.LLM_PROVIDER]


def build_chat_model(
    settings: Settings, *, temperature: float | None = None
) -> BaseChatModel:
    """Construct a LangChain chat model for the configured provider."""
    provider = settings.LLM_PROVIDER
    temp = settings.LLM_TEMPERATURE if temperature is None else temperature
    logger.info("llm.build_model", provider=provider.value)

    try:
        if provider is LLMProvider.OPENAI:
            from langchain_openai import ChatOpenAI

            if not settings.OPENAI_API_KEY:
                raise ExternalServiceError(
                    "OPENAI_API_KEY is not configured.", code="llm_misconfigured"
                )
            return ChatOpenAI(
                model=settings.OPENAI_MODEL,
                api_key=settings.OPENAI_API_KEY,
                temperature=temp,
            )

        if provider is LLMProvider.GEMINI:
            from langchain_google_genai import ChatGoogleGenerativeAI

            if not settings.GOOGLE_API_KEY:
                raise ExternalServiceError(
                    "GOOGLE_API_KEY is not configured.", code="llm_misconfigured"
                )
            return ChatGoogleGenerativeAI(
                model=settings.GEMINI_MODEL,
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=temp,
            )

        if provider is LLMProvider.OLLAMA:
            from langchain_ollama import ChatOllama

            return ChatOllama(
                model=settings.OLLAMA_MODEL,
                base_url=settings.OLLAMA_BASE_URL,
                temperature=temp,
            )
    except ImportError as exc:  # SDK for the selected provider not installed
        raise ExternalServiceError(
            f"LLM provider '{provider.value}' is selected but its SDK is not "
            f"installed: {exc}",
            code="llm_sdk_missing",
        ) from exc

    # Defensive: unreachable while the enum and branches stay in sync.
    raise ExternalServiceError(
        f"Unsupported LLM provider: {provider}", code="llm_unsupported"
    )
