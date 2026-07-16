import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.dependencies import get_sim_engine

def test_simulation_state_retrieval(client):
    """Verify that retrieval of current simulation state returns a valid schema."""
    response = client.get("/api/v1/simulation/state")
    assert response.status_code == 200
    data = response.json()
    assert "world" in data
    assert "ai" in data
    assert "attendance" in data["world"]["telemetry"]
    assert "active_alerts" in data["world"]["telemetry"]

def test_simulation_scenario_switching(client):
    """Verify that posting to start with a specific scenario updates the state."""
    # Start VIP Arrival scenario
    response = client.post("/api/v1/simulation/start", json={"scenario": "VIP Arrival"})
    assert response.status_code == 200
    assert response.json()["status"] == "started"
    assert response.json()["scenario"] == "VIP Arrival"

    # Verify that get state now reflects the VIP Arrival details
    state_resp = client.get("/api/v1/simulation/state")
    assert state_resp.status_code == 200
    state_data = state_resp.json()
    assert state_data["world"]["scenario"] == "VIP Arrival"
    
    # Check that the VIP alert is present
    alerts = state_data["world"]["telemetry"]["active_alerts"]
    vip_alert = any(a["id"] == "SEC-VIP" for a in alerts)
    assert vip_alert is True

def test_simulation_telemetry_generation(simulation_engine):
    """Verify SimulationEngine internally mutates values correctly and calculates metrics."""
    # Test initial base state calculation
    state = simulation_engine.get_state()
    assert state["scenario"] == "Normal Match"
    metrics = state["metrics"]
    assert metrics["incident_severity"] == "LOW"
    assert metrics["risk_score"] == 15

    # Switch scenario directly in the service
    simulation_engine.set_scenario("Power Failure")
    state_after = simulation_engine.get_state()
    assert state_after["scenario"] == "Power Failure"
    assert state_after["telemetry"]["power_status"] == "substation_failure"
    assert state_after["metrics"]["incident_severity"] == "CRITICAL"
    assert state_after["metrics"]["risk_score"] == 85

def test_invalid_scenario_handling(client):
    """Verify switching to an unknown or invalid scenario doesn't crash the server."""
    # The simulation engine resets to initial state for unknown scenarios
    response = client.post("/api/v1/simulation/start", json={"scenario": "Unknown Scenario Name"})
    assert response.status_code == 200
    assert response.json()["scenario"] == "Unknown Scenario Name"
    
    # State should fallback/reset safely
    state_resp = client.get("/api/v1/simulation/state")
    assert state_resp.status_code == 200
    assert state_resp.json()["world"]["scenario"] == "Unknown Scenario Name"
