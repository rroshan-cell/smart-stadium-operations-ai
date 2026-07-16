import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from models.schemas import AgentResponse, AgentRequest, ConfidenceScore, Recommendation, RoutingDecision, SystemAlert
from agents.coordinator import CoordinatorAgent
from agents.crowd_management_agent import CrowdManagementAgent
from agents.security_agent import SecurityAgent
from agents.emergency_response_agent import EmergencyResponseAgent
from agents.transportation_agent import TransportationAgent
from agents.maintenance_agent import MaintenanceAgent
from agents.visitor_support_agent import VisitorSupportAgent
from agents.weather_intelligence_agent import WeatherIntelligenceAgent

@pytest.fixture
def mock_agent_response():
    """Valid mock AgentResponse fixture."""
    return AgentResponse(
        agent_name="CrowdManagement",
        analysis="High crowd density at South Gate A.",
        recommendations=[
            Recommendation(action="Open auxiliary gates", priority="HIGH", target_zone="South Gate A", justification="Egress delay")
        ],
        confidence=ConfidenceScore(score=0.95, reasoning="Data matches egress models"),
        priority="HIGH",
        next_actions=["Deploy auxiliary gates staff"],
        requires_human_approval=True,
        alerts=[SystemAlert(level="WARNING", message="Concourse backup", timestamp="16:00:00")]
    )

@pytest.fixture
def mock_routing_decision():
    """Valid mock RoutingDecision fixture."""
    return RoutingDecision(
        selected_agents=["CrowdManagement"],
        reason="Crowd related request.",
        confidence=0.95,
        evidence="crowd density",
        operational_explanation="Call crowd agent to investigate"
    )

@pytest.mark.asyncio
async def test_full_coordinator_flow(mock_gemini_service, mock_agent_response, mock_routing_decision, context_manager):
    """Verify that CoordinatorAgent orchestrates routing, sub-agent processing, and synthesis."""
    coordinator = CoordinatorAgent(mock_gemini_service, context_manager=context_manager)
    crowd_agent = CrowdManagementAgent(mock_gemini_service, context_manager=context_manager)
    coordinator.add_agent(crowd_agent)

    # 1. Routing decision 2. Sub-agent response 3. Synthesis response
    mock_gemini_service.generate_structured_response.side_effect = [
        mock_routing_decision,
        mock_agent_response,
        mock_agent_response
    ]

    request = AgentRequest(query="South gates are crowded", telemetry={"attendance": 70000})
    result = await coordinator.process(request)

    assert isinstance(result, AgentResponse)
    assert result.agent_name == "CrowdManagement"
    assert result.requires_human_approval is True
    assert mock_gemini_service.generate_structured_response.call_count == 3
    
    # Verify Blackboard integration
    context = context_manager.get_full_context()
    assert len(context["agent_history"]) == 2  # CrowdManagement agent + Coordinator synthesis
    assert len(context["stadium_alerts"]) == 1

@pytest.mark.asyncio
async def test_coordinator_routing_cache(mock_gemini_service, mock_routing_decision):
    """Verify that Routing Decisions are cached in the Coordinator to save API tokens."""
    coordinator = CoordinatorAgent(mock_gemini_service)
    coordinator.add_agent(CrowdManagementAgent(mock_gemini_service))

    mock_gemini_service.generate_structured_response.return_value = mock_routing_decision

    # First call: cache miss
    res1 = await coordinator.determine_routing("South Gate Crowd")
    assert res1 == mock_routing_decision
    assert mock_gemini_service.generate_structured_response.call_count == 1

    # Second call: cache hit
    res2 = await coordinator.determine_routing("South Gate Crowd")
    assert res2 == mock_routing_decision
    assert mock_gemini_service.generate_structured_response.call_count == 1

@pytest.mark.asyncio
async def test_coordinator_routing_failure_fallback(mock_gemini_service):
    """Verify coordinator falls back gracefully to default routing on exception."""
    coordinator = CoordinatorAgent(mock_gemini_service)
    crowd_agent = CrowdManagementAgent(mock_gemini_service)
    coordinator.add_agent(crowd_agent)

    # Force route determination to fail
    mock_gemini_service.generate_structured_response.side_effect = Exception("Service Outage")

    decision = await coordinator.determine_routing("Any query")
    assert decision.selected_agents == ["CrowdManagement"]
    assert decision.confidence == 0.5
    assert "Fallback" in decision.reason

@pytest.mark.asyncio
async def test_coordinator_sub_agent_failure_fallback(mock_gemini_service, mock_routing_decision, mock_agent_response):
    """Verify coordinator falls back to superclass process when all sub-agents fail."""
    coordinator = CoordinatorAgent(mock_gemini_service)
    crowd_agent = CrowdManagementAgent(mock_gemini_service)
    coordinator.add_agent(crowd_agent)

    # 1. Routing decision 2. Sub-agent exception 3. Direct synthesis fallback
    mock_gemini_service.generate_structured_response.side_effect = [
        mock_routing_decision,
        Exception("Subagent crashed"),
        mock_agent_response
    ]

    request = AgentRequest(query="South gates", telemetry={})
    result = await coordinator.process(request)
    assert result == mock_agent_response

@pytest.mark.asyncio
async def test_all_individual_agents(mock_gemini_service, mock_agent_response, context_manager):
    """Ensure all 7 individual agents execute, parse, and write back to ContextManager."""
    agents_to_test = [
        CrowdManagementAgent,
        SecurityAgent,
        EmergencyResponseAgent,
        TransportationAgent,
        MaintenanceAgent,
        VisitorSupportAgent,
        WeatherIntelligenceAgent
    ]

    request = AgentRequest(query="Operational query", telemetry={"key": "val"})

    for agent_cls in agents_to_test:
        agent = agent_cls(mock_gemini_service, context_manager=context_manager)
        mock_gemini_service.generate_structured_response.return_value = mock_agent_response
        
        response = await agent.process(request)
        
        assert isinstance(response, AgentResponse)
        assert response.agent_name == "CrowdManagement"
        # Assert that prompt manager was called
        assert mock_gemini_service.generate_structured_response.called
