"""Itinerary prompt.

Drives generation of the recommendations + day-by-day plan. The output schema
(`ItineraryPlan`) is bound via structured output, so the prompt focuses on
*content quality* and leaves formatting to the schema.
"""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate

ITINERARY_SYSTEM_PROMPT = (
    "You are an expert travel itinerary planner. Produce a concrete, practical "
    "day-by-day plan plus useful recommendations for the trip described.\n\n"
    "Rules:\n"
    "- Produce exactly {num_days} day entries, numbered 1..{num_days}.\n"
    "- Each day needs a short theme title and 3-5 specific activities that "
    "suit the destination and the expected weather.\n"
    "- Recommendations should be practical: local food, getting around, "
    "safety, money, and packing notes — 4 to 6 items.\n"
    "- Be specific to the destination; avoid generic filler."
)


def build_itinerary_prompt() -> ChatPromptTemplate:
    """Chat prompt for itinerary + recommendations generation."""
    return ChatPromptTemplate.from_messages(
        [
            ("system", ITINERARY_SYSTEM_PROMPT),
            (
                "human",
                "Destination: {destination}\n"
                "From: {source}\n"
                "Trip length: {num_days} days\n"
                "Travelers: {travelers}\n"
                "Weather outlook: {weather}\n"
                "Plan the trip.",
            ),
        ]
    )
