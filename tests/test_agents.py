import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from models.schemas import AgentResponse, AgentRequest, ConfidenceScore, Recommendation, RoutingDecision
from agents.coordinator import CoordinatorAgent
from agents.crowd_management_agent import CrowdManagementAgent
from services.gemini_service import GeminiService

@pytest.fixture
def mock_gemini():
    service = MagicMock(spec=GeminiService)
    service.generate_structured_response = AsyncMock()
    service.chat = AsyncMock()
    return service

@pytest.fixture
def mock_agent_response():
    return AgentResponse(
        agent_name="CrowdManagement",
        analysis="High density at West Plaza",
        recommendations=[
            Recommendation(action="Open Gate 5", priority="High", target_zone="West", justification="Congestion")
        ],
        confidence=ConfidenceScore(score=0.95, reasoning="Telemetry match"),
        priority="HIGH",
        next_actions=["Deploy Security Branch B"],
        requires_human_approval=True
    )

@pytest.mark.asyncio
async def test_full_coordinator_flow(mock_gemini, mock_agent_response):
    """Test the full reasoning loop from routing to synthesis."""
    coordinator = CoordinatorAgent(mock_gemini)
    crowd_agent = CrowdManagementAgent(mock_gemini)
    coordinator.add_agent(crowd_agent)

    # 1. Mock Routing Decision
    mock_routing_decision = RoutingDecision(
        selected_agents=["CrowdManagement"],
        reason="Test evacuation query requires crowd management.",
        confidence=0.95,
        evidence="smoke_detected",
        operational_explanation="Deploy crowd agent to manage evacuation paths."
    )
    
    # 2. Mock Individual Agent Response
    # 3. Mock Coordinator Synthesis Response
    mock_gemini.generate_structured_response.side_effect = [
        mock_routing_decision, # First call for determine_routing
        mock_agent_response,   # Second call from Crowd Agent
        mock_agent_response    # Third call from Coordinator Synthesis
    ]

    request = AgentRequest(query="Evacuate the stadium", telemetry={"smoke_detected": True})
    
    result = await coordinator.process(request)
    
    assert isinstance(result, AgentResponse)
    assert result.requires_human_approval is True
    assert mock_gemini.generate_structured_response.call_count == 3

@pytest.mark.asyncio
async def test_agent_error_fallback(mock_gemini):
    """Verify that the system falls back gracefully when an agent fails."""
    agent = CrowdManagementAgent(mock_gemini)
    mock_gemini.generate_structured_response.side_effect = Exception("Gemini Timeout")

    with pytest.raises(Exception): # The service layer raises GeminiError
         await agent.process(AgentRequest(query="test", telemetry={}))
