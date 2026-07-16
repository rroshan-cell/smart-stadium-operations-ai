import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from backend.main import app
from services.context_manager import ContextManager
from services.simulation_engine import SimulationEngine
from services.gemini_service import GeminiService
from backend.dependencies import get_gemini_service, get_coordinator_agent
from agents.coordinator import CoordinatorAgent
from agents.crowd_management_agent import CrowdManagementAgent
from agents.security_agent import SecurityAgent
from agents.emergency_response_agent import EmergencyResponseAgent
from agents.transportation_agent import TransportationAgent
from agents.visitor_support_agent import VisitorSupportAgent
from agents.maintenance_agent import MaintenanceAgent
from agents.weather_intelligence_agent import WeatherIntelligenceAgent

@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    return TestClient(app)

@pytest.fixture
def mock_gemini_service():
    """Mock GeminiService fixture."""
    service = MagicMock(spec=GeminiService)
    service.generate_structured_response = AsyncMock()
    service.chat = AsyncMock()
    return service

@pytest.fixture
def context_manager():
    """Clean ContextManager instance fixture."""
    return ContextManager()

@pytest.fixture
def simulation_engine():
    """Clean SimulationEngine instance fixture."""
    return SimulationEngine()

@pytest.fixture
def override_dependencies(mock_gemini_service, context_manager):
    """Fixture to mock and override all FastAPI singleton dependencies globally."""
    mock_coordinator = CoordinatorAgent(mock_gemini_service, context_manager=context_manager)
    
    mock_coordinator.add_agent(CrowdManagementAgent(mock_gemini_service, context_manager=context_manager))
    mock_coordinator.add_agent(SecurityAgent(mock_gemini_service, context_manager=context_manager))
    mock_coordinator.add_agent(EmergencyResponseAgent(mock_gemini_service, context_manager=context_manager))
    mock_coordinator.add_agent(TransportationAgent(mock_gemini_service, context_manager=context_manager))
    mock_coordinator.add_agent(VisitorSupportAgent(mock_gemini_service, context_manager=context_manager))
    mock_coordinator.add_agent(MaintenanceAgent(mock_gemini_service, context_manager=context_manager))
    mock_coordinator.add_agent(WeatherIntelligenceAgent(mock_gemini_service, context_manager=context_manager))

    app.dependency_overrides[get_gemini_service] = lambda: mock_gemini_service
    app.dependency_overrides[get_coordinator_agent] = lambda: mock_coordinator
    yield mock_coordinator
    app.dependency_overrides.clear()
