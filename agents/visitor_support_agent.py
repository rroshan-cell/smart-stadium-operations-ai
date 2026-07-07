from .base_agent import BaseAgent, GeminiService

class VisitorSupportAgent(BaseAgent):
    def __init__(self, gemini_service: GeminiService):
        super().__init__(
            name="VisitorSupport",
            mission="Assist fans with wayfinding, accessibility, and info.",
            gemini_service=gemini_service
        )
