import os
from typing import TYPE_CHECKING
from .config import settings
from services.gemini_service import GeminiService
from services.context_manager import ContextManager
from agents.coordinator import CoordinatorAgent
from agents.crowd_management_agent import CrowdManagementAgent
from agents.security_agent import SecurityAgent
from agents.emergency_response_agent import EmergencyResponseAgent
from agents.transportation_agent import TransportationAgent
from agents.visitor_support_agent import VisitorSupportAgent
from agents.maintenance_agent import MaintenanceAgent
from agents.weather_intelligence_agent import WeatherIntelligenceAgent

if TYPE_CHECKING:
    from services.simulation_engine import SimulationEngine

# Singleton services
_gemini_service = None
_context_manager = None
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
        _gemini_service = GeminiService()
    return _gemini_service

def get_context_manager() -> ContextManager:
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
    return _context_manager

def get_coordinator_agent() -> CoordinatorAgent:
    global _coordinator
    if _coordinator is None:
        svc = get_gemini_service()
        ctx = get_context_manager()
        _coordinator = CoordinatorAgent(svc, context_manager=ctx)
        
        # Register all sub-agents, injecting the shared context manager
        _coordinator.add_agent(CrowdManagementAgent(svc, context_manager=ctx))
        _coordinator.add_agent(SecurityAgent(svc, context_manager=ctx))
        _coordinator.add_agent(EmergencyResponseAgent(svc, context_manager=ctx))
        _coordinator.add_agent(TransportationAgent(svc, context_manager=ctx))
        _coordinator.add_agent(VisitorSupportAgent(svc, context_manager=ctx))
        _coordinator.add_agent(MaintenanceAgent(svc, context_manager=ctx))
        _coordinator.add_agent(WeatherIntelligenceAgent(svc, context_manager=ctx))
        
    return _coordinator
