"""
Chat API route.
RAG-powered chat endpoint for the AI analyst assistant.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Will be set from main.py
chat_assistant = None


def set_assistant(assistant):
    global chat_assistant
    chat_assistant = assistant


class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


@router.post("")
async def chat(request: ChatMessage):
    """
    Send a question to the AI SOC analyst assistant.
    Uses RAG with recent alerts as context.
    """
    if chat_assistant is None:
        return {
            "response": "Chat assistant is not initialized. Please check backend configuration.",
            "context_alerts_used": 0,
        }

    try:
        response = await chat_assistant.chat(request.message)
        context_count = len(await chat_assistant.get_context_alerts())
        return {
            "response": response,
            "context_alerts_used": context_count,
        }
    except Exception as e:
        return {
            "response": f"I encountered an error processing your question: {str(e)}. Please try rephrasing.",
            "context_alerts_used": 0,
        }
