from fastapi import APIRouter
from pydantic import BaseModel
from backend.config import settings

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    version: str

@router.get("/", response_model=HealthResponse)
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}
