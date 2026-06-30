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
    "- Each day: a short theme title and exactly 3 activities. Keep each "
    "activity to a short phrase (max ~8 words) — no long sentences.\n"
    "- Provide exactly 4 brief recommendations (food, transport, safety, "
    "money/packing). One short line each.\n"
    "- Be specific to the destination; avoid filler. Be concise."
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
