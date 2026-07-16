import pytest
from services.prompt_manager import PromptManager

def test_prompt_manager_templates():
    """Verify that PromptManager returns prompts containing the mandatory structured schema directive."""
    agents = [
        "Coordinator",
        "CrowdManagement",
        "Security",
        "EmergencyResponse",
        "Transportation",
        "Maintenance",
        "VisitorSupport",
        "WeatherIntelligence"
    ]
    
    for agent in agents:
        prompt = PromptManager.get_prompt(
            agent,
            query="Test Query",
            telemetry="Test Telemetry",
            history="Test History",
            shared_context="Test Context"
        )
        assert isinstance(prompt, str)
        assert "CRITICAL: Return ONLY valid JSON matching the AgentResponse schema" in prompt
        assert "agent_name" in prompt
        assert "analysis" in prompt

def test_prompt_manager_fallback():
    """Verify that PromptManager falls back cleanly for unregistered agents."""
    prompt = PromptManager.get_prompt("UnknownAgent", query="Hello")
    assert "You are a General Stadium Assistant." in prompt
    assert "Hello" in prompt

def test_prompt_manager_missing_variables():
    """Verify formatting replaces missing kwargs with default placeholders."""
    # When variables like telemetry are missing
    prompt = PromptManager.get_prompt("VisitorSupport", query="Help")
    assert "[not provided]" in prompt
    assert "Help" in prompt
