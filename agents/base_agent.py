from typing import Any, Dict, Optional
from models.schemas import AgentResponse, AgentRequest
from services.gemini_service import GeminiService
from services.prompt_manager import PromptManager
from services.context_manager import ContextManager
from backend.logger import logger

class BaseAgent:
    def __init__(self, name: str, mission: str, gemini_service: GeminiService, context_manager: Optional[ContextManager] = None):
        self.name = name
        self.mission = mission
        self.gemini_service = gemini_service
        self.context_manager = context_manager

    async def process(self, request: AgentRequest) -> AgentResponse:
        """Core processing logic using GeminiService with shared ContextManager integration."""
        logger.info(f"Agent {self.name} processing query: {request.query}")
        
        shared_ctx_dict = {}
        if self.context_manager:
            shared_ctx_dict = self.context_manager.get_full_context()

            # Do not expose previous AI conversation to the LLM
            shared_ctx_dict.pop("ai_decisions", None)
            shared_ctx_dict.pop("agent_outputs", None)
            shared_ctx_dict.pop("conversation", None)
            shared_ctx_dict.pop("chat_history", None)
            shared_ctx_dict.pop("messages", None)
            
            # Log reading shared memory
            logger.debug(f"Agent {self.name} read blackboard memory with last update: {shared_ctx_dict.get('last_update')}")

        # Construct prompt, injecting query, telemetry, history, and shared context
        prompt = PromptManager.get_prompt(
            self.name,
            query=request.query,
            telemetry=request.telemetry,
            history=request.history,
            shared_context=shared_ctx_dict
        )

        response = await self.gemini_service.generate_structured_response(
            prompt=prompt,
            response_model=AgentResponse
        )

        # Write results back to ContextManager (Blackboard)
        if self.context_manager:
            logger.info(f"Agent {self.name} writing decisions and alerts back to blackboard.")
            self.context_manager.add_agent_output(self.name, response.model_dump())
            
            # If the response generates alerts, merge them into the blackboard alert system
            if response.alerts:
                self.context_manager.merge_alerts([a.model_dump() for a in response.alerts])

        return response
