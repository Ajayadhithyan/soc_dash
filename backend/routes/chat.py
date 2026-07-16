"""
Chat API route.
RAG-powered chat endpoint for the AI analyst assistant.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from backend.models.schemas import ChatRequest, ChatResponse
from backend.services.auth import optional_current_user
from backend.services.container import get_chat_assistant

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    chat_assistant=Depends(get_chat_assistant),
    current_user: dict = Depends(optional_current_user),
):
    if chat_assistant is None:
        return ChatResponse(
            response="Chat assistant is not initialized. Please check backend configuration.",
            context_alerts_used=0,
        )

    try:
        response = await chat_assistant.chat(request.message)
        context_count = len(await chat_assistant.get_context_alerts())
        return ChatResponse(response=response, context_alerts_used=context_count)
    except Exception as e:
        return ChatResponse(
            response=f"I encountered an error processing your question: {str(e)}. Please try rephrasing.",
            context_alerts_used=0,
        )
