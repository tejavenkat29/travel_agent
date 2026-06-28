"""Chat domain value objects.

Framework-free representations of a conversation. They carry no knowledge of
HTTP (Pydantic), of LangChain, or of any specific LLM provider — that mapping
happens in the outer layers. This is the vocabulary the rest of the app speaks.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Role(str, Enum):
    """Author of a chat message."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass(frozen=True)
class Message:
    """A single turn in a conversation."""

    role: Role
    content: str


@dataclass(frozen=True)
class ChatResult:
    """The outcome of an LLM call."""

    content: str
    provider: str
    model: str
