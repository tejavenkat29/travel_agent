"""Planner Agent prompts.

The system prompt steers extraction behaviour; the structured-output schema
(`TripParameters`) supplies the exact field shape, so this prompt deliberately
contains no JSON formatting instructions — those are injected automatically by
`with_structured_output`.
"""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate

PLANNER_SYSTEM_PROMPT = (
    "You are the Planner Agent of an AI travel planner. Your only job is to "
    "extract structured trip parameters from the user's request.\n\n"
    "Rules:\n"
    "- Extract: destination, source, budget, currency, number of days, and "
    "number of travelers.\n"
    "- Only use information explicitly stated or strongly implied by the "
    "user. If a field is not mentioned, leave it null — never guess or "
    "fabricate values.\n"
    "- 'source' is where the user departs FROM; 'destination' is where they "
    "go TO. Do not swap them.\n"
    "- For budget, return the numeric amount and capture its currency code "
    "separately (default to USD only if a currency symbol like '$' is used "
    "without other context).\n"
    "- 'travelers' is the total count of people on the trip."
)


def build_planner_prompt() -> ChatPromptTemplate:
    """Chat prompt for trip-parameter extraction."""
    return ChatPromptTemplate.from_messages(
        [
            ("system", PLANNER_SYSTEM_PROMPT),
            ("human", "{request}"),
        ]
    )
