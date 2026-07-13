import os
import asyncio
# pyrefly: ignore [missing-import]
import google.generativeai as genai
from typing import Optional, Type, TypeVar
from pydantic import BaseModel
from backend.config import settings
from backend.logger import logger
from backend.exceptions import GeminiError
from .response_parser import ResponseParser

T = TypeVar("T", bound=BaseModel)

class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.error("GEMINI_API_KEY is missing")
            raise GeminiError("Gemini API key not configured")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)

    async def generate_structured_response(
        self, 
        prompt: str, 
        response_model: Type[T],
        retries: int = 2,
        timeout_seconds: int = 30
    ) -> T:
        """
        Generate a response from Gemini and validate it against a Pydantic model.
        Includes automatic retry logic and structured logging.
        """
        attempt = 0
        last_error = None

        while attempt < retries:
            try:
                logger.info(f"Gemini Request (Attempt {attempt+1}): {prompt[:100]}...")
                
                # Execute Gemini call in a thread pool to avoid blocking async loop if SDK is synchronous
                # Note: Most of genai SDK is currently blocking, so we wrap it
                loop = asyncio.get_event_loop()
                response = await asyncio.wait_for(
                    loop.run_in_executor(None, lambda: self.model.generate_content(prompt)),
                    timeout=timeout_seconds
                )

                if not response or not response.text:
                    raise GeminiError("Empty response from Gemini")

                # Parse and validate
                structured_data = ResponseParser.validate_response(response.text, response_model)
                logger.info(f"Gemini Success: {response_model.__name__} validated")
                return structured_data

            except asyncio.TimeoutError:
                last_error = "Gemini request timed out"
                logger.warning(f"Timeout on attempt {attempt+1}")
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Gemini error on attempt {attempt+1}: {last_error}")
            
            attempt += 1
            if attempt < retries:
                # Exponential backoff
                await asyncio.sleep(2 ** attempt)

        raise GeminiError(f"Failed to generate structured response after {retries} retries: {last_error}")

    async def chat(self, message: str, history: Optional[list] = None) -> str:
        """Simple text-based chat interface."""
        try:
            chat_session = self.model.start_chat(history=history or [])
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: chat_session.send_message(message)
            )
            return response.text
        except Exception as e:
            logger.error(f"Chat failed: {str(e)}")
            raise GeminiError("Failed to communicate with Gemini")
