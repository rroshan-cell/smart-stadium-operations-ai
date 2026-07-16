import os
import json
from typing import Optional, Type, TypeVar

from groq import Groq
from pydantic import BaseModel

from backend.config import settings
from backend.exceptions import GeminiError
from backend.logger import logger

T = TypeVar("T", bound=BaseModel)


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
            messages = [
                {
                    "role": "system",
                    "content": """
You are StadiumOps AI, the Incident Commander for MetLife Stadium during the FIFA World Cup 2026.

Stay completely in character.

Rules:
- Never behave like ChatGPT.
- Never mention being an AI language model.
- Respond only as the Stadium Command Center.
- Be concise and operational.
- Base decisions only on the supplied telemetry.
- Do not invent incidents.
- Keep responses under 400 words.

Structure every response using:

🚨 SITUATION ASSESSMENT

⚠ OPERATIONAL RISKS

🎯 IMMEDIATE ACTIONS

🚔 SECURITY & MEDICAL

🚍 TRANSPORTATION

📢 PUBLIC COMMUNICATION

Use short tactical bullet points wherever possible.
""",
                }
            ]

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
                                "content": str(content),
                            }
                        )

            messages.append(
                {
                    "role": "user",
                    "content": message,
                }
            )

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2,
                max_tokens=500,
            )

            return completion.choices[0].message.content

        except Exception as e:
            logger.exception("Groq chat failed")
            raise GeminiError(str(e))

    async def generate_structured_response(
        self,
        prompt: str,
        response_model: Type[T],
    ) -> T:
        """
        Generates structured JSON output that matches a Pydantic model.
        """

        try:
            schema = response_model.model_json_schema()

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"""
You are StadiumOps AI.

Generate ONLY valid JSON matching the provided schema.

Requirements:
- Never return markdown.
- Never return explanations.
- Never return code fences.
- Keep all text concise.
- Base every decision only on the supplied telemetry.
- Do not invent incidents.

Narrative fields should contain short operational summaries only.

Schema:

Return ONLY valid JSON matching this schema:

{json.dumps(schema, indent=2)}

Do not return markdown code blocks (e.g. ```json).
Do not explain anything.
Return JSON only.
""",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0.1,
                max_tokens=500,
                response_format={"type": "json_object"},
            )

            text = completion.choices[0].message.content

            logger.info("Structured response generated successfully.")

            data = json.loads(text)

            return response_model.model_validate(data)

        except Exception as e:
            logger.exception("Groq structured generation failed")
            raise GeminiError(str(e))