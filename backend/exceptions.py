from fastapi import Request, status
from fastapi.responses import JSONResponse
from typing import Any, Dict

class AppError(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR, details: Any = None):
        self.message = message
        self.status_code = status_code
        self.details = details

class AgentError(AppError):
    pass

class GeminiError(AppError):
    pass

async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details,
            "status": "failed"
        }
    )

async def global_exception_handler(request: Request, exc: Exception):
    # Log the full traceback here in production
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "An unexpected error occurred into the system.",
            "status": "error"
        }
    )
