import asyncio
import json
import time
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentResponse, AgentRequest
from models.schemas import RoutingDecision, ConfidenceScore
from services.gemini_service import GeminiService
from services.context_manager import ContextManager
from backend.logger import logger

class CoordinatorAgent(BaseAgent):
    def __init__(self, gemini_service: GeminiService, context_manager: Optional[ContextManager] = None):
        super().__init__(
            name="Coordinator",
            mission="Analyze intent and orchestrate specialized agents.",
            gemini_service=gemini_service,
            context_manager=context_manager
        )
        self.agents: Dict[str, BaseAgent] = {}
        self.routing_cache: Dict[str, RoutingDecision] = {}  # In-memory routing cache

    def add_agent(self, agent: BaseAgent):
        self.agents[agent.name] = agent

    async def determine_routing(self, query: str) -> RoutingDecision:
        """Use Gemini to decide which agents are relevant and generate an explainable routing decision with caching."""
        cache_key = query.strip().lower()
        if cache_key in self.routing_cache:
            logger.info(f"Routing cache hit for query: '{query}'")
            return self.routing_cache[cache_key]

        logger.info(f"Routing cache miss. Coordinator determining routing for query: '{query}'")
        
        prompt = f"""
        Analyze this stadium operations query: "{query}"
        Available Agents: {list(self.agents.keys())}
        
        Determine which specialized agents are required to handle this operational query.
        For each selection, evaluate the telemetry indicators or keywords in the query to provide evidence, confidence level, reason, and operational explanation.
        
        Example: Medical emergency -> EmergencyResponse (high priority medical dispatch), Security (area lockdown / route clearing), Transportation (ambulance egress lanes).
        """
        try:
            routing_decision = await self.gemini_service.generate_structured_response(
                prompt=prompt,
                response_model=RoutingDecision
            )
            # Filter selected agents to ensure they are registered
            valid_agents = [name for name in routing_decision.selected_agents if name in self.agents]
            if not valid_agents:
                valid_agents = [list(self.agents.keys())[0]] if self.agents else ["VisitorSupport"]
            routing_decision.selected_agents = valid_agents
            
            # Save to routing cache
            self.routing_cache[cache_key] = routing_decision
            return routing_decision
        except Exception as e:
            logger.error(f"Structured routing failed, falling back. Error: {str(e)}")
            fallback_agent = [list(self.agents.keys())[0]] if self.agents else ["VisitorSupport"]
            fallback_decision = RoutingDecision(
                selected_agents=fallback_agent,
                reason="Fallback routing due to structured generator failure.",
                confidence=0.5,
                evidence="System error / fallback",
                operational_explanation="Directing query to default available agent."
            )
            return fallback_decision

    async def process(self, request: AgentRequest) -> AgentResponse:
        start_time = time.time()
        logger.info(f"Coordinator analyzing query: {request.query}")

        # Record telemetry snapshot in ContextManager (Blackboard) before starting execution
        if self.context_manager:
            self.context_manager.add_telemetry_snapshot(request.telemetry)
            self.context_manager.add_timeline_event(f"Coordinator received query: '{request.query}'")

        # 1. Determine Routing (Explainable AI Routing)
        routing_decision = await self.determine_routing(request.query)
        selected_agent_names = routing_decision.selected_agents
        logger.info(f"Explainable routing decision: {routing_decision.model_dump()}")

        # Save routing decision in ContextManager
        if self.context_manager:
            self.context_manager.update_state("routing_decision", routing_decision.model_dump())
            self.context_manager.add_timeline_event(
                f"Routed to {selected_agent_names}. Rationale: {routing_decision.reason}"
            )

        # 2. Parallel execution of routed agents
        tasks = [self.agents[name].process(request) for name in selected_agent_names]
        agent_responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Gather successful responses
        successful_responses = []
        for name, resp in zip(selected_agent_names, agent_responses):
            if isinstance(resp, AgentResponse):
                successful_responses.append(resp)
            else:
                logger.error(f"Sub-agent {name} failed execution: {str(resp)}")

        if not successful_responses:
            logger.warning("No sub-agents succeeded. Falling back to direct Coordinator reasoning.")
            fallback_response = await super().process(request)
            fallback_response.routing_decision = routing_decision
            return fallback_response

        # 3. Merging & Conflict Resolution
        reports_json = json.dumps(
            [r.model_dump() for r in successful_responses],
            default=str,
            indent=2
        )

        synthesis_prompt = f"""
        You are the FIFA Stadium Operations Director at MetLife Stadium.
        Synthesize the following specialist agent reports into a single, unified command directive:
        REPORTS: {reports_json}
        QUERY: {request.query}
        
        CRITICAL RULES:
        1. Resolve any conflicting directions: prioritize safety, threat lockdown, and emergency dispatch over standard flow or visitor support.
        2. Merge identical or duplicate recommendations into single concise actions.
        3. Formulate a final unified command plan with a clear hierarchy of priorities.
        4. Exclude duplicate alerts and ensure any critical alerts are bubbled up to the top level.
        """

        final_decision = await self.gemini_service.generate_structured_response(
            prompt=synthesis_prompt,
            response_model=AgentResponse
        )

        # Inject the explainable routing decision for the UI/dashboard
        final_decision.routing_decision = routing_decision

        # Record final decision to Blackboard and timeline
        if self.context_manager:
            self.context_manager.add_agent_output(self.name, final_decision.model_dump())
            self.context_manager.add_timeline_event(f"Coordinator synthesized final plan with priority {final_decision.priority}")
            
            # Record any final alerts to ContextManager
            if final_decision.alerts:
                self.context_manager.merge_alerts([a.model_dump() for a in final_decision.alerts])

        # Log total execution time
        end_time = time.time()
        logger.info(f"Coordinator successfully processed request in {end_time - start_time:.4f}s")

        return final_decision
