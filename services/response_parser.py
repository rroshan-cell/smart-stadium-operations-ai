import json
import re
from typing import Type, TypeVar
from pydantic import BaseModel, ValidationError
from backend.logger import logger

T = TypeVar("T", bound=BaseModel)

class ResponseParser:
    @staticmethod
    def parse_json(content: str) -> dict:
        """Attempt to extract and parse JSON from LLM response."""
        try:
            # Try direct parse
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to find JSON block
            match = re.search(r'\{(?:[^{}]|(?R))*\}', content, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except:
                    pass
            
            # Simple manual repair for common LLM issues (trailing commas, etc)
            content = re.sub(r',\s*\}', '}', content)
            content = re.sub(r',\s*\]', ']', content)
            try:
                return json.loads(content)
            except:
                raise ValueError("Could not parse or repair JSON from LLM response")

    @classmethod
    def validate_response(cls, content: str, model: Type[T]) -> T:
        """Parse and validate content against a Pydantic model."""
        try:
            raw_data = cls.parse_json(content)
            return model.validate(raw_data)
        except (ValueError, ValidationError) as e:
            logger.error(f"Response parsing failed: {str(e)}")
            raise e
