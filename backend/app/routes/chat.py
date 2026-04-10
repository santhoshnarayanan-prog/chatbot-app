import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.ai_service import get_ai_response

logger = logging.getLogger(__name__)
router = APIRouter()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, strip_whitespace=True)


class ChatResponse(BaseModel):
    response: str


@router.post("/", response_model=ChatResponse)
async def chat_api(request: ChatRequest):
    try:
        reply = await get_ai_response(request.message)
        return ChatResponse(response=reply)
    except Exception as e:
        logger.error("Chat endpoint error: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An error occurred processing your request.",
        )
