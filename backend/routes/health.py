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


@router.get("/groq-debug")
def groq_debug():
    import os
    from backend.config import settings

    return {
        "has_key": bool(settings.GROQ_API_KEY),
        "key_prefix": settings.GROQ_API_KEY[:10] if settings.GROQ_API_KEY else None,
        "env_key": bool(os.getenv("GROQ_API_KEY")),
        "model": settings.AI_MODEL
    }    