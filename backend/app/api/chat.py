import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from app.api.auth_middleware import get_current_user
from app.services.agent_service import AgentService

logger = logging.getLogger(__name__)

router = APIRouter()
agent_service = AgentService()

class ChatMessage(BaseModel):
    role: str
    parts: List[str]

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    history: Optional[List[ChatMessage]] = Field(default=None, max_length=50)

@router.post("/")
async def chat_with_agent(
    payload: ChatRequest,
    user_id: str = Depends(get_current_user),
):
    try:
        formatted_history = []
        if payload.history:
            for msg in payload.history:
                formatted_history.append({
                    "role": msg.role,
                    "parts": msg.parts
                })

        response_text = await agent_service.chat(
            user_id=user_id,
            message=payload.message,
            history=formatted_history
        )
        return {"response": response_text}
    except Exception as e:
        logger.exception("Chat failed for user %s: %s", user_id, e)
        raise HTTPException(status_code=500, detail="Chat service temporarily unavailable. Please try again.")
