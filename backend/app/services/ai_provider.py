import asyncio
import logging
import os
from abc import ABC, abstractmethod
from typing import Dict, List

logger = logging.getLogger(__name__)


class AIProvider(ABC):
    @abstractmethod
    async def complete(self, messages: List[Dict]) -> str:
        pass


class GroqProvider(AIProvider):
    def __init__(self):
        from groq import Groq
        self._client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        logger.info("Initialized Groq provider — model: %s", self.model)

    async def complete(self, messages: List[Dict]) -> str:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self._client.chat.completions.create(
                model=self.model,
                messages=messages,
            ),
        )
        return response.choices[0].message.content


class OpenAIProvider(AIProvider):
    def __init__(self):
        from openai import OpenAI
        self._client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        logger.info("Initialized OpenAI provider — model: %s", self.model)

    async def complete(self, messages: List[Dict]) -> str:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self._client.chat.completions.create(
                model=self.model,
                messages=messages,
            ),
        )
        return response.choices[0].message.content


def get_provider() -> AIProvider:
    """Factory — set AI_PROVIDER=groq (default) or AI_PROVIDER=openai in .env."""
    name = os.getenv("AI_PROVIDER", "groq").lower()
    if name == "openai":
        return OpenAIProvider()
    return GroqProvider()
