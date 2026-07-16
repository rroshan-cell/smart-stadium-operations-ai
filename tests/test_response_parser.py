import pytest
from pydantic import BaseModel, ValidationError
from services.response_parser import ResponseParser

class SimpleModel(BaseModel):
    key: str
    value: int

def test_parse_json_valid():
    """Verify parse_json parses valid JSON strings directly."""
    content = '{"key": "test", "value": 123}'
    res = ResponseParser.parse_json(content)
    assert res == {"key": "test", "value": 123}

def test_parse_json_with_fences():
    """Verify parse_json removes markdown code fences and returns parsed JSON."""
    content = '```json\n{"key": "test", "value": 123}\n```'
    res = ResponseParser.parse_json(content)
    assert res == {"key": "test", "value": 123}

def test_parse_json_extracted():
    """Verify parse_json extracts JSON object nested within other text."""
    content = 'Leading chatter {"key": "test", "value": 123} trailing details'
    res = ResponseParser.parse_json(content)
    assert res == {"key": "test", "value": 123}

def test_parse_json_repaired():
    """Verify parse_json repairs common syntax issues like trailing commas."""
    content = '{"key": "test", "value": 123,}'
    res = ResponseParser.parse_json(content)
    assert res == {"key": "test", "value": 123}

def test_parse_json_invalid():
    """Verify parse_json raises ValueError for completely unparsable text."""
    with pytest.raises(ValueError) as exc:
        ResponseParser.parse_json("This has no JSON block at all")
    assert "Could not parse or repair JSON" in str(exc.value)

def test_validate_response_success():
    """Verify validate_response parses and instantiates the Pydantic schema model."""
    content = '{"key": "test", "value": 123}'
    obj = ResponseParser.validate_response(content, SimpleModel)
    assert isinstance(obj, SimpleModel)
    assert obj.key == "test"
    assert obj.value == 123

def test_validate_response_validation_error():
    """Verify validate_response propagates ValidationError when schema validation fails."""
    content = '{"key": "test", "value": "not-an-int"}'
    with pytest.raises(ValidationError):
        ResponseParser.validate_response(content, SimpleModel)
