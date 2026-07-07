from .base_agent import BaseAgent, GeminiService

class EmergencyResponseAgent(BaseAgent):
    def __init__(self, gemini_service: GeminiService):
        super().__init__(
            name="EmergencyResponse",
            mission="Rapid life-safety and medical resource coordination.",
            gemini_service=gemini_service
        )
