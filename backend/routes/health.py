from fastapi import APIRouter
import os

from backend.config import settings
from models.schemas import HealthResponse

router = APIRouter()

@router.get("/", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="healthy",
        version=settings.VERSION
    )

@router.get("/gemini-debug")
def gemini_debug():
    return {
        "has_env_key": bool(os.getenv("GEMINI_API_KEY")),
        "has_settings_key": bool(settings.GEMINI_API_KEY),
        "model": settings.GEMINI_MODEL
    }