from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any, List
from ..dependencies import get_coordinator_agent
from agents.coordinator import CoordinatorAgent
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
    # Call the actual coordinator process
    agent_request = AgentRequest(
        query=request.query,
        telemetry=request.telemetry_snapshot
    )
    result = await coordinator.process(agent_request)
    return result

@router.get("/status")
async def get_stadium_status():
    return {
        "attendance": 78642,
        "capacity_pct": 95.3,
        "active_alerts": 3,
        "avg_queue_time": "3m 45s",
        "parking_occupancy": 84,
        "ai_confidence": 0.98,
        "gates": {
            "gate-a": "red",
            "gate-b": "green",
            "gate-c": "yellow",
            "gate-d": "green"
        }
    }

@router.get("/alerts")
async def get_active_alerts():
    return [
        {
            "id": "INC-001",
            "title": "Medical: Cardiac Sector 112",
            "priority": "critical",
            "area": "Sector 112",
            "action": "MedTeam 3 dispatched. Eta 2m.",
            "confidence": 0.99,
            "timestamp": "21:00"
        },
        {
            "id": "INC-002",
            "title": "Gate C Congestion",
            "priority": "warning",
            "area": "Gate C",
            "action": "Opening Overflow Gate 2. Redirect signage active.",
            "confidence": 0.92,
            "timestamp": "20:58"
        }
    ]
