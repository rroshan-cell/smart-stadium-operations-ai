import os
# pyrefly: ignore [missing-import]
import google.generativeai as genai
from .config import settings
from services.gemini_service import GeminiService
from agents.coordinator import CoordinatorAgent
from agents.crowd_management_agent import CrowdManagementAgent
from agents.security_agent import SecurityAgent
from agents.emergency_response_agent import EmergencyResponseAgent
from agents.transportation_agent import TransportationAgent
from agents.visitor_support_agent import VisitorSupportAgent
from agents.maintenance_agent import MaintenanceAgent
from agents.weather_intelligence_agent import WeatherIntelligenceAgent

# Singleton services
_gemini_service = None
_coordinator = None
_sim_engine = None

def get_sim_engine() -> "SimulationEngine":
    global _sim_engine
    if _sim_engine is None:
        from services.simulation_engine import SimulationEngine
        _sim_engine = SimulationEngine()
    return _sim_engine

def get_gemini_service() -> GeminiService:
    global _gemini_service
    if _gemini_service is None:
        api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
        _gemini_service = GeminiService()
    return _gemini_service

def get_coordinator_agent() -> CoordinatorAgent:
    global _coordinator
    if _coordinator is None:
        svc = get_gemini_service()
        _coordinator = CoordinatorAgent(svc)
        
        # Register all sub-agents
        _coordinator.add_agent(CrowdManagementAgent(svc))
        _coordinator.add_agent(SecurityAgent(svc))
        _coordinator.add_agent(EmergencyResponseAgent(svc))
        _coordinator.add_agent(TransportationAgent(svc))
        _coordinator.add_agent(VisitorSupportAgent(svc))
        _coordinator.add_agent(MaintenanceAgent(svc))
        _coordinator.add_agent(WeatherIntelligenceAgent(svc))
        
    return _coordinator
