from fastapi import APIRouter
# pyrefly: ignore [missing-import]
from .health import router as health_router
# pyrefly: ignore [missing-import]
from .chat import router as chat_router
# pyrefly: ignore [missing-import]
from .agents import router as agents_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(chat_router, prefix="/chat", tags=["ai", "chat"])
api_router.include_router(agents_router, prefix="/agents", tags=["agents"])
