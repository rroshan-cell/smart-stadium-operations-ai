import json
import re
from typing import Type, TypeVar
from pydantic import BaseModel, ValidationError
from backend.logger import logger

T = TypeVar("T", bound=BaseModel)

class ResponseParser:
    @staticmethod
    def _extract_json_object(content: str) -> str | None:
        """Find the first complete JSON object or array in content by tracking brace depth."""
        for start_char, end_char in [('{', '}'), ('[', ']')]:
            start = content.find(start_char)
            if start == -1:
                continue
            depth = 0
            for i, ch in enumerate(content[start:], start=start):
                if ch == start_char:
                    depth += 1
                elif ch == end_char:
                    depth -= 1
                    if depth == 0:
                        return content[start:i + 1]
        return None

    @staticmethod
    def parse_json(content: str) -> dict:
        """Attempt to extract and parse JSON from LLM response."""
        # Strip markdown code fences if present
        content = re.sub(r'^```(?:json)?\s*', '', content.strip(), flags=re.MULTILINE)
        content = re.sub(r'\s*```$', '', content.strip(), flags=re.MULTILINE)

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # Try to find JSON block by bracket depth tracking
        extracted = ResponseParser._extract_json_object(content)
        if extracted:
            try:
                return json.loads(extracted)
            except json.JSONDecodeError:
                pass

        # Simple manual repair for common LLM issues (trailing commas, etc.)
        repaired = re.sub(r',\s*}', '}', content)
        repaired = re.sub(r',\s*]', ']', repaired)
        try:
            return json.loads(repaired)
        except json.JSONDecodeError:
            raise ValueError("Could not parse or repair JSON from LLM response")

    @classmethod
    def validate_response(cls, content: str, model: Type[T]) -> T:
        """Parse and validate content against a Pydantic model."""
        try:
            raw_data = cls.parse_json(content)
            return model.model_validate(raw_data)
        except (ValueError, ValidationError) as e:
            logger.error(f"Response parsing failed: {str(e)}")
            raise e
