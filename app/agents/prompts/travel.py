"""Reusable travel-assistant prompts.

Centralises every prompt the travel assistant uses so wording lives in one
place (not scattered through code) and can be reviewed, versioned and reused.

Demonstrates both LangChain prompt primitives:
- `PromptTemplate`      — a single-string template (completion style).
- `ChatPromptTemplate`  — a multi-message template (system + human), the form
                          used with chat models.
"""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

# --- System instruction shared by the chat prompt -------------------------
TRAVEL_SYSTEM_PROMPT = (
    "You are an expert travel assistant. Recommend a single destination that "
    "best fits the user's request, budget and trip length. Be concrete and "
    "practical. Respond ONLY with data in the requested format — no prose, no "
    "markdown fences."
)

# --- PromptTemplate: simple, single-string template -----------------------
# Useful for completion-style models or as a building block. `{...}` slots are
# filled at call time via `.format(...)` / `.invoke(...)`.
TRAVEL_QUERY_TEMPLATE: PromptTemplate = PromptTemplate.from_template(
    "Recommend a travel destination.\n"
    "Request: {query}\n"
    "Trip length: {duration_days} days\n"
    "Budget: {budget}"
)


def build_travel_chat_prompt(format_instructions: str) -> ChatPromptTemplate:
    """Build the chat prompt, pre-filling the parser's format instructions.

    `format_instructions` comes from the output parser and tells the model the
    exact JSON shape to return. We bind it now with `.partial(...)` so callers
    only need to supply the runtime variables (`query`, `duration_days`,
    `budget`).
    """
    return ChatPromptTemplate.from_messages(
        [
            ("system", TRAVEL_SYSTEM_PROMPT + "\n\n{format_instructions}"),
            (
                "human",
                "Request: {query}\n"
                "Trip length: {duration_days} days\n"
                "Budget: {budget}",
            ),
        ]
    ).partial(format_instructions=format_instructions)
