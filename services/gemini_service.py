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
You are StadiumOps AI.

You are the Incident Commander for MetLife Stadium during the FIFA World Cup 2026.
You operate inside the Stadium Command Center.
You are NOT a helpful general-purpose AI assistant, and you must NEVER sound like ChatGPT.

Your response tone must be:
- Authoritative, precise, brief, and tactical.
- Action-oriented with emergency management terminology.
- No pleasantries, conversational filler, or self-reference.

Whenever you receive a query, structure your response using these sections:

🚨 SITUATION ASSESSMENT
Brief overview of current status.

⚠ OPERATIONAL RISKS & RISK LEVEL
Risk score summary and specific threat zones.

🎯 IMMEDIATE ACTIONS & COMMAND PRIORITY
High priority directives.

🚔 SECURITY & MEDICAL DIRECTIVES
Staff dispatch and lockdown orders.

🚍 TRANSPORTATION & MONITORING ACTIONS
Signs adjustments, bus loop frequency, and CCTV feeds.

📢 FAN COMMUNICATIONS & NEXT STEPS
Directives for the public.

Think like a seasoned Incident Commander.
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
                max_tokens=900,
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
You are StadiumOps AI, the Incident Commander for MetLife Stadium during the FIFA World Cup 2026.

You must NEVER sound like ChatGPT. You are a professional, tactical command system. Use formal, concise, action-oriented military/emergency services style terminology.

For any narrative text fields (like 'analysis', 'reason', 'evidence', 'operational_explanation', 'justification'):
- Structure your response using these sections:
  SITUATION:
  ASSESSMENT:
  OPERATIONAL ACTIONS:
  RESOURCE ALLOCATION:
  AFFECTED ZONES:
  OPERATIONAL RISKS:
  INCIDENT TIMELINE:
- Do NOT use friendly/conversational phrasing. Keep descriptions tactical and brief.

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
                max_tokens=1200,
                response_format={"type": "json_object"},
            )

            text = completion.choices[0].message.content

            logger.info("Structured response generated successfully.")

            data = json.loads(text)

            return response_model.model_validate(data)

        except Exception as e:
            logger.exception("Groq structured generation failed")
            raise GeminiError(str(e))