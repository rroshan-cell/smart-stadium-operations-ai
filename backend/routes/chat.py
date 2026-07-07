from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from ..dependencies import get_gemini_service
from services.gemini_service import GeminiService

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    stream: bool = False

class ChatResponse(BaseModel):
    response: str
    context_used: Optional[List[str]] = []

@router.post("/", response_model=ChatResponse)
async def chat_with_gemini(
    request: ChatRequest,
    gemini: GeminiService = Depends(get_gemini_service)
):
    # Call the actual gemini service
    response_text = await gemini.chat(request.message)
    return {"response": response_text, "context_used": ["stadium_blueprints"]}
