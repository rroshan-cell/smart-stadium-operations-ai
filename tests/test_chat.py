import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from models.schemas import AgentResponse, ConfidenceScore, Recommendation, SystemAlert, RoutingDecision
from backend.main import app

def test_chat_valid_request(client, mock_gemini_service, override_dependencies):
    """Verify chat endpoint processes a valid request with appropriate mocks."""
    routing_decision = RoutingDecision(
        selected_agents=["CrowdManagement"],
        reason="Request for evacuation details",
        confidence=0.95,
        evidence="evacuation",
        operational_explanation="Coordinate crowd flow"
    )
    
    agent_response = AgentResponse(
        agent_name="CrowdManagement",
        analysis="Egress pathways are congested.",
        recommendations=[
            Recommendation(action="Open Gate C immediately", priority="CRITICAL", target_zone="Gate C", justification="High density concourse")
        ],
        confidence=ConfidenceScore(score=0.98, reasoning="Telemetry verified"),
        priority="CRITICAL",
        next_actions=["Dispatch crowd supervisors"],
        requires_human_approval=True,
        alerts=[SystemAlert(level="CRITICAL", message="Evacuation bottleneck", timestamp="12:00:00")]
    )
    
    # Coordinator routes -> Crowd agent processes -> Coordinator synthesizes
    mock_gemini_service.generate_structured_response.side_effect = [
        routing_decision,
        agent_response,
        agent_response
    ]
    
    payload = {"message": "Evacuation instructions"}
    response = client.post("/api/v1/chat/", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "context_used" in data
    assert "SITUATION ASSESSMENT" in data["response"]
    assert "OPERATIONAL COMMANDS" in data["response"]
    assert "ACTIVE ALERTS" in data["response"]
    assert "AI CONFIDENCE" in data["response"]

def test_chat_empty_message(client, mock_gemini_service, override_dependencies):
    """Verify posting an empty message is handled safely and outputs standard template."""
    routing_decision = RoutingDecision(
        selected_agents=["VisitorSupport"],
        reason="Fallback routing for empty message",
        confidence=0.5,
        evidence="empty query",
        operational_explanation="Directing query to default available agent."
    )
    
    agent_response = AgentResponse(
        agent_name="VisitorSupport",
        analysis="No message query provided.",
        recommendations=[],
        confidence=ConfidenceScore(score=1.0, reasoning="Default fallback"),
        priority="MEDIUM",
        next_actions=[],
        requires_human_approval=False,
        alerts=[]
    )
    
    mock_gemini_service.generate_structured_response.side_effect = [
        routing_decision,
        agent_response,
        agent_response
    ]

    payload = {"message": ""}
    response = client.post("/api/v1/chat/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data

def test_chat_malformed_payload(client):
    """Verify malformed payload returns 422 Unprocessable Entity."""
    response = client.post("/api/v1/chat/", json={"msg": "Invalid field name"})
    assert response.status_code == 422

    response = client.post("/api/v1/chat/", data="invalid-json-content")
    assert response.status_code == 422

def test_chat_long_message(client, mock_gemini_service, override_dependencies):
    """Verify chat endpoint handles extremely long inputs robustly."""
    routing_decision = RoutingDecision(
        selected_agents=["VisitorSupport"],
        reason="General status request",
        confidence=0.8,
        evidence="query",
        operational_explanation="Address long message request"
    )
    
    agent_response = AgentResponse(
        agent_name="VisitorSupport",
        analysis="Normal operations.",
        recommendations=[],
        confidence=ConfidenceScore(score=0.9, reasoning="No anomalies detected"),
        priority="MEDIUM",
        next_actions=[],
        requires_human_approval=False,
        alerts=[]
    )
    
    mock_gemini_service.generate_structured_response.side_effect = [
        routing_decision,
        agent_response,
        agent_response
    ]

    long_message = "status " * 1000
    response = client.post("/api/v1/chat/", json={"message": long_message})
    assert response.status_code == 200
