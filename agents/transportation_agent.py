from .base_agent import BaseAgent, GeminiService

class TransportationAgent(BaseAgent):
    def __init__(self, gemini_service: GeminiService):
        super().__init__(
            name="Transportation",
            mission="Optimize transit flow and parking lot capacity.",
            gemini_service=gemini_service
        )
