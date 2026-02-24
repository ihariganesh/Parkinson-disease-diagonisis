"""
Chatbot API — Powered by local Llama 3.2 via Ollama
Provides health-related Q&A for Parkinson's patients
"""

from fastapi import APIRouter, Depends, Body
from pydantic import BaseModel
from typing import Optional, List, Dict
from app.db.models import User
from app.core.security import get_current_user
from app.services.ollama_service import chatbot_ask, check_ollama_health

router = APIRouter()


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = None


@router.post("/ask")
async def ask_chatbot(
    message: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
):
    """Ask the AI chatbot a health-related question using local Llama 3.2."""
    try:
        user_name = f"{current_user.first_name} {current_user.last_name}".strip() or current_user.email.split("@")[0]

        reply = await chatbot_ask(
            message=message,
            user_name=user_name,
        )

        return {"reply": reply}

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Chatbot error: {e}")
        return {
            "reply": "I'm sorry, an unexpected error occurred. Please make sure Ollama is running with Llama 3.2."
        }


@router.post("/chat")
async def chat_with_history(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """Chat with conversation history support, powered by Llama 3.2."""
    try:
        user_name = f"{current_user.first_name} {current_user.last_name}".strip() or current_user.email.split("@")[0]

        # Convert history to the format ollama_service expects
        history = None
        if request.history:
            history = [{"role": msg.role, "content": msg.content} for msg in request.history]

        reply = await chatbot_ask(
            message=request.message,
            user_name=user_name,
            conversation_history=history,
        )

        return {"reply": reply}

    except Exception as e:
        print(f"Chat error: {e}")
        return {
            "reply": "I'm sorry, an unexpected error occurred. Please try again."
        }


@router.get("/status")
async def chatbot_status():
    """Check if the chatbot (Ollama + Llama 3.2) is available."""
    available = await check_ollama_health()
    return {
        "available": available,
        "engine": "Llama 3.2 (Ollama)" if available else "Unavailable",
        "message": "Chatbot is ready" if available else "Ollama is not running. Please start Ollama with 'ollama serve'.",
    }
