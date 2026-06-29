"""Travel-assistant chain (LangChain Expression Language).

Assembles the end-to-end pipeline as a `RunnableSequence`:

        prompt  |  model  |  parser

- `prompt`  formats the request into chat messages (ChatPromptTemplate).
- `model`   is any LangChain chat model (OpenAI/Gemini/Ollama) — itself a
            Runnable, so it composes with `|`.
- `parser`  is a `PydanticOutputParser` that turns the model's text reply into
            a validated `TravelRecommendation` instance.

`build_travel_chain(model)` takes the model as an argument so the chain is
trivially testable with a fake/stub Runnable; `build_travel_chain_from_settings`
wires in the real provider via the existing factory.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import Runnable

from app.agents.prompts.travel import build_travel_chat_prompt
from app.core.config import Settings
from app.infrastructure.llm.factory import build_chat_model
from app.schemas.travel import TravelRecommendation

if TYPE_CHECKING:
    from langchain_core.language_models.chat_models import BaseChatModel


def get_travel_output_parser() -> PydanticOutputParser:
    """OutputParser that validates LLM text into `TravelRecommendation`."""
    return PydanticOutputParser(pydantic_object=TravelRecommendation)


def build_travel_chain(model: BaseChatModel | Runnable) -> Runnable:
    """Compose `prompt | model | parser` into a single Runnable."""
    parser = get_travel_output_parser()
    prompt = build_travel_chat_prompt(parser.get_format_instructions())
    # The `|` operator builds a RunnableSequence — data flows left to right.
    return prompt | model | parser


def build_travel_chain_from_settings(settings: Settings) -> Runnable:
    """Build the chain backed by the configured LLM provider."""
    return build_travel_chain(build_chat_model(settings))
