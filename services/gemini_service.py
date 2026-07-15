import os
from typing import Optional

from groq import Groq

from backend.config import settings
from backend.exceptions import GeminiError
from backend.logger import logger


class GeminiService:
    """
    Uses Groq internally while keeping the same class name so the
    rest of the project remains unchanged.
    """

    def __init__(self):
        self.api_key = settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY")

        if not self.api_key:
            raise GeminiError("GROQ_API_KEY not configured")

        self.client = Groq(api_key=self.api_key)
        self.model = settings.AI_MODEL

    async def chat(self, message: str, history: Optional[list] = None) -> str:
        try:
            messages = []

            if history:
                for item in history:
                    if isinstance(item, dict):
                        role = item.get("role", "user")
                        content = item.get("parts") or item.get("content", "")
                        if isinstance(content, list):
                            content = " ".join(str(x) for x in content)
                        messages.append(
                            {
                                "role": role,
                                "content": str(content)
                            }
                        )

            messages.append(
                {
                    "role": "user",
                    "content": message
                }
            )

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=800
            )

            return completion.choices[0].message.content

        except Exception as e:
            logger.exception("Groq chat failed")
            raise GeminiError(str(e))