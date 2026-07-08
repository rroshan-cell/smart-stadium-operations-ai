from fastapi import APIRouter

from .health import router as health_router
from .chat import router as chat_router
from .agents import router as agents_router
from .simulation import router as simulation_router

api_router = APIRouter()

api_router.include_router(
    health_router,
    prefix="/health",
    tags=["health"]
)

api_router.include_router(
    chat_router,
    prefix="/chat",
    tags=["ai", "chat"]
)

api_router.include_router(
    agents_router,
    prefix="/agents",
    tags=["agents"]
)

api_router.include_router(
    simulation_router,
    prefix="/simulation",
    tags=["simulation"]
)