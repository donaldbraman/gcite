"""
Base agent class for Gemini AI agents.
Provides common functionality for all agents.
"""

import google.generativeai as genai
import logging
from typing import Optional
from config.settings import settings

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for Gemini AI agents."""

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the base agent.

        Args:
            model_name: Optional model name override
        """
        self.model_name = model_name or settings.GEMINI_MODEL

        # Configure Gemini API
        if settings.GOOGLE_GENAI_API_KEY:
            genai.configure(api_key=settings.GOOGLE_GENAI_API_KEY)
            self.model = genai.GenerativeModel(self.model_name)
            self.enabled = True
            logger.info(f"Agent initialized with model: {self.model_name}")
        else:
            self.model = None
            self.enabled = False
            logger.warning("Gemini API key not configured - agent disabled")

    async def generate_content(
        self,
        prompt: str,
        temperature: float = 0.1,
        max_output_tokens: int = 500
    ) -> Optional[str]:
        """
        Generate content using Gemini.

        Args:
            prompt: The prompt to send to Gemini
            temperature: Temperature for generation (0.0-1.0)
            max_output_tokens: Maximum tokens to generate

        Returns:
            Generated text or None if error
        """
        if not self.enabled:
            logger.warning("Agent not enabled - no API key")
            return None

        try:
            response = await self.model.generate_content_async(
                prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_output_tokens
                }
            )
            return response.text

        except Exception as e:
            logger.error(f"Gemini API error: {e}", exc_info=True)
            return None


# Dependency for FastAPI
def get_agent_enabled() -> bool:
    """Check if agents are enabled."""
    return bool(settings.GOOGLE_GENAI_API_KEY)
