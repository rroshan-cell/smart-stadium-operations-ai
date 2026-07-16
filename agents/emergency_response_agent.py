from typing import Optional
from .base_agent import BaseAgent, GeminiService
from services.context_manager import ContextManager

class EmergencyResponseAgent(BaseAgent):
    def __init__(self, gemini_service: GeminiService, context_manager: Optional[ContextManager] = None):
        super().__init__(
            name="EmergencyResponse",
            mission="Rapid life-safety and medical resource coordination.",
            gemini_service=gemini_service,
            context_manager=context_manager
        )
