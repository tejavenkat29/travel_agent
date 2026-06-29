"""LangSmith observability.

Two pieces:

1. `configure_observability()` — called at startup. When tracing is enabled in
   settings, it exports the `LANGCHAIN_*` environment variables the LangChain /
   LangGraph SDKs read. With these set, **every** LangChain runnable and
   LangGraph node is traced automatically: prompts, responses, token usage and
   per-step latency are captured and shipped to LangSmith. No per-call code.

2. `traceable(...)` — a thin wrapper over `langsmith.traceable` used to trace
   the *non-LLM* agents (flight/hotel/weather/budget), which aren't LangChain
   runnables, so they still show up as spans. It degrades gracefully to a no-op
   decorator if `langsmith` isn't installed, so the app never hard-depends on it.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any, TypeVar

from app.core.config import Settings, settings as _settings
from app.core.logging import get_logger

logger = get_logger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def configure_observability(settings: Settings | None = None) -> None:
    """Export LangSmith env vars based on settings (idempotent)."""
    cfg = settings or _settings

    if not (cfg.LANGCHAIN_TRACING_V2 and cfg.LANGCHAIN_API_KEY):
        # Explicitly off so a stray env var can't enable partial tracing.
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
        logger.info("observability.disabled")
        return

    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = cfg.LANGCHAIN_ENDPOINT
    os.environ["LANGCHAIN_API_KEY"] = cfg.LANGCHAIN_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = cfg.LANGCHAIN_PROJECT
    logger.info("observability.enabled", project=cfg.LANGCHAIN_PROJECT)


def traceable(*d_args: Any, **d_kwargs: Any) -> Callable[[F], F]:
    """Decorator that records a function as a LangSmith run.

    Falls back to an identity decorator when `langsmith` isn't installed, so the
    same code runs with or without the observability dependency.
    """

    def decorator(func: F) -> F:
        try:
            from langsmith import traceable as ls_traceable
        except Exception:  # langsmith not installed
            return func
        return ls_traceable(*d_args, **d_kwargs)(func)

    return decorator
