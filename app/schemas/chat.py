"""Chat API schemas (request/response contracts for `POST /chat`)."""

from pydantic import BaseModel, Field

from app.domain.entities.chat import Role


class ChatMessageSchema(BaseModel):
    """One message in the conversation sent by the client."""

    role: Role = Field(..., description="Who authored the message")
    content: str = Field(..., min_length=1, description="Message text")


class ChatRequest(BaseModel):
    """Body for `POST /chat`."""

    messages: list[ChatMessageSchema] = Field(
        ..., min_length=1, description="Conversation history, oldest first"
    )
    temperature: float | None = Field(
        default=None,
        ge=0.0,
        le=2.0,
        description="Optional sampling override for this request",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "messages": [
                    {"role": "system", "content": "You are a travel assistant."},
                    {"role": "user", "content": "Suggest 3 cities for a beach trip."},
                ],
                "temperature": 0.2,
            }
        }
    }


class ChatResponse(BaseModel):
    """Response body for `POST /chat`."""

    content: str = Field(..., description="The assistant's reply")
    provider: str = Field(..., description="LLM provider that served the request")
    model: str = Field(..., description="Concrete model used")

    model_config = {
        "json_schema_extra": {
            "example": {
                "content": "Lisbon, Barcelona and Nice are great beach options...",
                "provider": "openai",
                "model": "gpt-4o",
            }
        }
    }
