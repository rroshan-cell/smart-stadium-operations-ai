import asyncio
import json
from typing import Dict, Any
from .base_agent import BaseAgent, AgentResponse, AgentRequest
from services.gemini_service import GeminiService
from services.prompt_manager import PromptManager
from backend.logger import logger

class CoordinatorAgent(BaseAgent):
    def __init__(self, gemini_service: GeminiService):
        super().__init__(
            name="Coordinator",
            mission="Analyze intent and orchestrate specialized agents.",
            gemini_service=gemini_service
        )
        self.agents: Dict[str, BaseAgent] = {}

    def add_agent(self, agent: BaseAgent):
        self.agents[agent.name] = agent

    async def determine_routing(self, query: str) -> list[str]:
        """Use Gemini to decide which agents are relevant."""
        prompt = f"""
        Analyze this stadium operations query: "{query}"
        Available Agents: {list(self.agents.keys())}
        Identify which agents should handle this. Return only a comma-separated list of agent names.
        Example: Medical emergency -> EmergencyResponse, Security, Transportation
        """
        response = await self.gemini_service.chat(prompt)
        selected = [name.strip() for name in response.split(",") if name.strip() in self.agents]
        return selected or ["VisitorSupport"]  # Fallback

    async def process(self, request: AgentRequest) -> AgentResponse:
        logger.info(f"Coordinator analyzing query: {request.query}")

        # 1. Routing
        selected_agent_names = await self.determine_routing(request.query)
        logger.info(f"Routing to agents: {selected_agent_names}")

        # 2. Parallel Execution
        tasks = [self.agents[name].process(request) for name in selected_agent_names]
        agent_responses = await asyncio.gather(*tasks, return_exceptions=True)

        # 3. Merging & Conflict Resolution
        successful_responses = [resp for resp in agent_responses if isinstance(resp, AgentResponse)]

        if not successful_responses:
            return await super().process(request)  # Fallback to direct Coordinator reasoning

        # Serialize responses to JSON for the LLM instead of Python repr
        reports_json = json.dumps(
            [r.model_dump() for r in successful_responses],
            default=str,
            indent=2
        )

        synthesis_prompt = f"""
        Synthesize the following agent reports into a single operational response:
        REPORTS: {reports_json}
        QUERY: {request.query}
        Resolve any conflicting directions and provide a unified command plan.
        """

        final_decision = await self.gemini_service.generate_structured_response(
            prompt=synthesis_prompt,
            response_model=AgentResponse
        )

        return final_decision
