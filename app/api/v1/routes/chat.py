"""Chat endpoint — `POST /api/v1/chat`.

A thin presentation-layer handler: it converts the validated request into
domain `Message`s, delegates to the injected `AbstractLLMService`, and maps the
domain `ChatResult` back to the response schema. It contains no provider logic
and no business rules.
"""

from fastapi import APIRouter, Depends

from app.api.v1.dependencies import get_llm_service
from app.domain.entities.chat import Message
from app.domain.interfaces.llm import AbstractLLMService
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(tags=["chat"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Chat with the configured LLM",
    description="Sends a conversation to the active LLM provider "
    "(OpenAI/Gemini/Ollama) and returns the reply.",
)
async def chat(
    request: ChatRequest,
    service: AbstractLLMService = Depends(get_llm_service),
) -> ChatResponse:
    messages = [Message(role=m.role, content=m.content) for m in request.messages]
    result = await service.chat(messages, temperature=request.temperature)
    return ChatResponse(
        content=result.content, provider=result.provider, model=result.model
    )
