from .base_agent import BaseAgent, GeminiService

class CrowdManagementAgent(BaseAgent):
    def __init__(self, gemini_service: GeminiService):
        super().__init__(
            name="CrowdManagement",
            mission="Prevent congestion and ensure safe spectator flow.",
            gemini_service=gemini_service
        )
