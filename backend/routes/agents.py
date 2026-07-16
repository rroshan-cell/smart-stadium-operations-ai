from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any, List
from ..dependencies import get_coordinator_agent, get_sim_engine
from agents.coordinator import CoordinatorAgent
from services.simulation_engine import SimulationEngine
from models.schemas import AgentRequest

router = APIRouter()

class AgentRoutingRequest(BaseModel):
    query: str
    telemetry_snapshot: Dict[str, Any]

class AgentRoutingResponse(BaseModel):
    selected_agents: List[str]
    plan: str
    priority: str

@router.post("/route")
async def route_to_agents(
    request: AgentRoutingRequest,
    coordinator: CoordinatorAgent = Depends(get_coordinator_agent)
):
    agent_request = AgentRequest(
        query=request.query,
        telemetry=request.telemetry_snapshot
    )
    result = await coordinator.process(agent_request)
    return result

@router.get("/status")
async def get_stadium_status(
    sim_engine: SimulationEngine = Depends(get_sim_engine)
):
    """Returns live stadium status enriched with advanced operational metrics."""
    state = sim_engine.get_state()
    telemetry = state["telemetry"]
    metrics = state["metrics"]
    num_alerts = len(telemetry.get("active_alerts", []))
    
    return {
        "attendance": int(telemetry.get("attendance", 70000)),
        "capacity_pct": metrics.get("crowd_density"),
        "active_alerts": num_alerts,
        "avg_queue_time": telemetry.get("avg_queue_time", 3),
        "parking_occupancy": metrics.get("parking_utilization"),
        "ai_confidence": metrics.get("ai_confidence"),
        "scenario": state.get("scenario", "Normal Match"),
        "gates": telemetry.get("gates", {
            "gate-a": "green",
            "gate-b": "green",
            "gate-c": "green",
            "gate-d": "green"
        }),
        # Advanced operational metrics
        "risk_score": metrics.get("risk_score"),
        "crowd_density": metrics.get("crowd_density"),
        "incident_severity": metrics.get("incident_severity"),
        "queue_prediction": metrics.get("queue_prediction"),
        "response_time": metrics.get("response_time"),
        "parking_utilization": metrics.get("parking_utilization"),
        "fan_zone_load": metrics.get("fan_zone_load"),
        "gate_utilization": metrics.get("gate_utilization"),
        "weather_risk": metrics.get("weather_risk"),
        "emergency_readiness": metrics.get("emergency_readiness"),
        "evacuation_readiness": metrics.get("evacuation_readiness"),
        "command_readiness": metrics.get("command_readiness")
    }

@router.get("/alerts")
async def get_active_alerts(
    sim_engine: SimulationEngine = Depends(get_sim_engine)
):
    """Returns active alerts from the live simulation engine plus any static standing alerts."""
    state = sim_engine.get_state()
    telemetry = state["telemetry"]
    sim_alerts = telemetry.get("active_alerts", [])

    enriched = []
    for alert in sim_alerts:
        enriched.append({
            "id": alert.get("id", "SIM-001"),
            "title": alert.get("title", "Simulation Alert"),
            "priority": alert.get("priority", "warning"),
            "area": alert.get("area", "Stadium General"),
            "action": alert.get("action", "AI agents are monitoring the situation."),
            "confidence": 0.95,
            "timestamp": alert.get("timestamp", ""),
            "message": alert.get("message", "")
        })

    return enriched
