from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from models.schemas import AgentResponse, AgentRequest
from services.gemini_service import GeminiService
from services.prompt_manager import PromptManager

class BaseAgent(ABC):
    def __init__(self, name: str, mission: str, gemini_service: GeminiService):
        self.name = name
        self.mission = mission
        self.gemini_service = gemini_service

    async def process(self, request: AgentRequest) -> AgentResponse:
        """Core processing logic using GeminiService."""
        prompt = PromptManager.get_prompt(
            self.name, 
            query=request.query, 
            telemetry=request.telemetry,
            history=request.history
        )
        
        response = await self.gemini_service.generate_structured_response(
            prompt=prompt,
            response_model=AgentResponse
        )
        return response
