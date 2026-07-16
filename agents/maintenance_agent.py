from typing import Optional
from .base_agent import BaseAgent, GeminiService
from services.context_manager import ContextManager

class MaintenanceAgent(BaseAgent):
    def __init__(self, gemini_service: GeminiService, context_manager: Optional[ContextManager] = None):
        super().__init__(
            name="Maintenance",
            mission="Monitor infrastructure and dispatch facility crews.",
            gemini_service=gemini_service,
            context_manager=context_manager
        )
