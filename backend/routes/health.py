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

    if os.getenv("ENVIRONMENT") == "production":
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Debug endpoint disabled in production.")

    return {
        "has_key": bool(settings.GROQ_API_KEY),
        "api_configured": bool(settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None,
        "env_key": bool(os.getenv("GROQ_API_KEY")),
        "model": settings.AI_MODEL
    }    