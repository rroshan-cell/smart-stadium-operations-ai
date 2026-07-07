from .base_agent import BaseAgent, GeminiService

class WeatherIntelligenceAgent(BaseAgent):
    def __init__(self, gemini_service: GeminiService):
        super().__init__(
            name="WeatherIntelligence",
            mission="Integrate climate data into safety protocols.",
            gemini_service=gemini_service
        )
