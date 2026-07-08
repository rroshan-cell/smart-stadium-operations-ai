from fastapi import APIRouter, Body, Depends
from services.simulation_engine import SimulationEngine
from ..dependencies import get_sim_engine

router = APIRouter()

@router.post("/start")
async def start_simulation(
    scenario: str = Body(..., embed=True),
    sim_engine: SimulationEngine = Depends(get_sim_engine)
):
    """
    Start or switch the simulation scenario.
    """
    sim_engine.set_scenario(scenario)

    return {
        "status": "started",
        "scenario": scenario
    }


@router.get("/state")
async def get_simulation_state(
    sim_engine: SimulationEngine = Depends(get_sim_engine)
):
    """
    Returns the latest stadium simulation state.

    IMPORTANT:
    This endpoint is intentionally Gemini-free because the dashboard
    polls it frequently. AI reasoning should be triggered only through
    chat or dedicated agent endpoints.
    """

    state = sim_engine.get_state()

    return {
        "world": state,
        "ai": {
            "analysis": (
                "Stadium operations are stable. No critical incidents detected. "
                "Telemetry is being monitored continuously."
            ),
            "recommendations": [
                "Continue monitoring crowd density.",
                "Maintain normal security patrols.",
                "Monitor weather updates.",
                "Keep transportation routes under observation."
            ],
            "next_actions": [
                "No immediate action required."
            ],
            "confidence": {
                "score": 0.95
            }
        }
    }