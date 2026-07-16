import time
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from backend.main import app, rate_limit_storage
from backend.dependencies import get_gemini_service
from models.schemas import AgentResponse, ConfidenceScore, Recommendation, RoutingDecision

def test_api_404_not_found(client):
    """Verify requesting an unregistered route returns 404."""
    response = client.get("/api/v1/non-existent-route")
    assert response.status_code == 404

def test_api_422_validation_error(client):
    """Verify malformed inputs generate a 422 error via Pydantic."""
    response = client.post("/api/v1/agents/route", json={"query": "test"})  # missing telemetry_snapshot
    assert response.status_code == 422

def test_api_process_time_header(client):
    """Verify that logging/profiling middlewares append X-Request-ID and X-Process-Time."""
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert "X-Process-Time" in response.headers

def test_api_rate_limiting(client):
    """Verify that rate limiter middleware triggers a 429 when thresholds are crossed."""
    # Inject values directly to trigger limit for TestClient's default IP "testclient"
    rate_limit_storage["testclient"] = [time.time()] * 100
    
    response = client.get("/api/v1/health/")
    assert response.status_code == 429
    assert response.json()["error"] == "Too many requests. Please wait a minute."
    
    # Cleanup rate limit storage
    rate_limit_storage.clear()

def test_agents_status_endpoint(client):
    """Verify status endpoint returns all advanced operational metrics correctly."""
    response = client.get("/api/v1/agents/status")
    assert response.status_code == 200
    data = response.json()
    assert "attendance" in data
    assert "risk_score" in data
    assert "avg_queue_time" in data
    assert "parking_occupancy" in data

def test_agents_alerts_endpoint(client):
    """Verify alerts endpoint extracts active simulation alerts successfully."""
    response = client.get("/api/v1/agents/alerts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_agents_routing_post_endpoint(client, mock_gemini_service, override_dependencies):
    """Verify routing requests are processed and returned successfully using mocked dependencies."""
    routing_decision = RoutingDecision(
        selected_agents=["Security"],
        reason="Security assessment",
        confidence=0.9,
        evidence="smoke",
        operational_explanation="Deploy security agent"
    )
    
    agent_response = AgentResponse(
        agent_name="Security",
        analysis="Security breach check",
        recommendations=[],
        confidence=ConfidenceScore(score=0.9, reasoning="Telemetry match"),
        priority="HIGH",
        next_actions=[],
        requires_human_approval=False,
        alerts=[]
    )
    
    mock_gemini_service.generate_structured_response.side_effect = [
        routing_decision,
        agent_response,
        agent_response
    ]
    
    payload = {
        "query": "Drone intrusion at South Gate A",
        "telemetry_snapshot": {"attendance": 70000}
    }
    response = client.post("/api/v1/agents/route", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["agent_name"] == "Security"
