from fastapi.testclient import TestClient

def test_health_check(client):
    """Verify that the health check endpoint returns 200 and is healthy."""
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data

def test_groq_debug(client, monkeypatch):
    """Verify the groq-debug settings endpoint returns expected configurations."""
    monkeypatch.setenv("GROQ_API_KEY", "test_key_123")
    
    # Reload settings configuration inside test context if settings are cached, or mock settings directly
    from backend.config import settings
    monkeypatch.setattr(settings, "GROQ_API_KEY", "test_key_123")
    
    response = client.get("/api/v1/health/groq-debug")
    assert response.status_code == 200
    data = response.json()
    assert data["has_key"] is True
    assert data["api_configured"] is True
    assert data["env_key"] is True
    assert data["model"] == "llama-3.3-70b-versatile"
