from fastapi import APIRouter, Depends, Body
from services.simulation_engine import SimulationEngine
from agents.coordinator import CoordinatorAgent
from backend.dependencies import get_coordinator_agent
from models.schemas import AgentRequest

router = APIRouter()
_sim_engine = SimulationEngine()

@router.post("/start")
async def start_simulation(scenario: str = Body(..., embed=True)):
    _sim_engine.set_scenario(scenario)
    return {"status": "started", "scenario": scenario}

@router.get("/state")
async def get_simulation_state(coordinator: CoordinatorAgent = Depends(get_coordinator_agent)):
    state = _sim_engine.get_state()
    
    # Automatically trigger AI reasoning based on the current telemetry
    agent_request = AgentRequest(
        query=f"Analyze current stadium state for scenario: {state['scenario']}",
        telemetry=state['telemetry']
    )
    
    # The coordinator selected agents and produces a master response
    ai_analysis = await coordinator.process(agent_request)
    
    return {
        "world": state,
        "ai": ai_analysis
    }
