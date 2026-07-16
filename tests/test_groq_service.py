import pytest
import json
from unittest.mock import MagicMock, patch
from pydantic import BaseModel
from services.gemini_service import GeminiService
from backend.exceptions import GeminiError

class DummySchema(BaseModel):
    name: str
    score: int

def test_gemini_service_init_missing_key(monkeypatch):
    """Verify GeminiService initialization fails when GROQ_API_KEY is not configured."""
    from backend.config import settings
    monkeypatch.setattr(settings, "GROQ_API_KEY", None)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    
    with pytest.raises(GeminiError) as exc:
        GeminiService()
    assert "GROQ_API_KEY not configured" in str(exc.value)

@pytest.mark.asyncio
async def test_gemini_service_chat_success(monkeypatch):
    """Verify chat returns completion text on successful API call."""
    from backend.config import settings
    monkeypatch.setattr(settings, "GROQ_API_KEY", "mock_key")
    
    # Mock client and its creation path
    mock_client = MagicMock()
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock()]
    mock_completion.choices[0].message.content = "Operational Response text"
    mock_client.chat.completions.create.return_value = mock_completion
    
    with patch("services.gemini_service.Groq", return_value=mock_client):
        service = GeminiService()
        result = await service.chat("Hello test", history=[{"role": "user", "content": "Hi"}])
        assert result == "Operational Response text"
        mock_client.chat.completions.create.assert_called_once()

@pytest.mark.asyncio
async def test_gemini_service_chat_exception(monkeypatch):
    """Verify chat failure raises a GeminiError."""
    from backend.config import settings
    monkeypatch.setattr(settings, "GROQ_API_KEY", "mock_key")
    
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("API connection timed out")
    
    with patch("services.gemini_service.Groq", return_value=mock_client):
        service = GeminiService()
        with pytest.raises(GeminiError) as exc:
            await service.chat("test")
        assert "API connection timed out" in str(exc.value)

@pytest.mark.asyncio
async def test_gemini_service_structured_success(monkeypatch):
    """Verify structured response parser outputs validated Pydantic models."""
    from backend.config import settings
    monkeypatch.setattr(settings, "GROQ_API_KEY", "mock_key")
    
    mock_client = MagicMock()
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock()]
    mock_completion.choices[0].message.content = json.dumps({"name": "Test User", "score": 95})
    mock_client.chat.completions.create.return_value = mock_completion
    
    with patch("services.gemini_service.Groq", return_value=mock_client):
        service = GeminiService()
        result = await service.generate_structured_response("Test prompt", DummySchema)
        assert isinstance(result, DummySchema)
        assert result.name == "Test User"
        assert result.score == 95

@pytest.mark.asyncio
async def test_gemini_service_structured_failure(monkeypatch):
    """Verify exception in structured responder raises a GeminiError."""
    from backend.config import settings
    monkeypatch.setattr(settings, "GROQ_API_KEY", "mock_key")
    
    mock_client = MagicMock()
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock()]
    # Return malformed JSON that fails parsing
    mock_completion.choices[0].message.content = "Malformed JSON Text"
    mock_client.chat.completions.create.return_value = mock_completion
    
    with patch("services.gemini_service.Groq", return_value=mock_client):
        service = GeminiService()
        with pytest.raises(GeminiError):
            await service.generate_structured_response("Test prompt", DummySchema)
