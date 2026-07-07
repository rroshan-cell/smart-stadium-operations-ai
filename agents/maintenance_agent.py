from .base_agent import BaseAgent, GeminiService

class MaintenanceAgent(BaseAgent):
    def __init__(self, gemini_service: GeminiService):
        super().__init__(
            name="Maintenance",
            mission="Monitor infrastructure and dispatch facility crews.",
            gemini_service=gemini_service
        )
