from typing import Optional
from .base_agent import BaseAgent, GeminiService
from services.context_manager import ContextManager

class CrowdManagementAgent(BaseAgent):
    def __init__(self, gemini_service: GeminiService, context_manager: Optional[ContextManager] = None):
        super().__init__(
            name="CrowdManagement",
            mission="Prevent congestion and ensure safe spectator flow.",
            gemini_service=gemini_service,
            context_manager=context_manager
        )
