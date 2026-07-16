from typing import Optional
from .base_agent import BaseAgent, GeminiService
from services.context_manager import ContextManager

class WeatherIntelligenceAgent(BaseAgent):
    def __init__(self, gemini_service: GeminiService, context_manager: Optional[ContextManager] = None):
        super().__init__(
            name="WeatherIntelligence",
            mission="Integrate climate data into safety protocols.",
            gemini_service=gemini_service,
            context_manager=context_manager
        )
