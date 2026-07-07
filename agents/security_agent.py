from .base_agent import BaseAgent, GeminiService

class SecurityAgent(BaseAgent):
    def __init__(self, gemini_service: GeminiService):
        super().__init__(
            name="Security",
            mission="Venue safety, incident triage, and risk assessment.",
            gemini_service=gemini_service
        )
