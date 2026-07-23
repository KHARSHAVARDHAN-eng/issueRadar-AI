import logging

from app.core.config import settings
from app.services.ai.base_provider import BaseLLMProvider
from app.services.ai.gemini_provider import GeminiProvider
from app.services.ai.mock_provider import MockLLMProvider
from app.services.ai.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)


class AIProviderFactory:
    """Factory creating and caching LLM Provider instances based on configuration."""

    _instances: dict[str, BaseLLMProvider] = {}

    @classmethod
    def get_provider(cls, provider_type: str | None = None) -> BaseLLMProvider:
        name = (provider_type or settings.AI_PROVIDER).lower().strip()

        if name not in cls._instances:
            if name == "gemini":
                logger.info("Instantiating GeminiProvider")
                cls._instances[name] = GeminiProvider()
            elif name == "openai":
                logger.info("Instantiating OpenAIProvider")
                cls._instances[name] = OpenAIProvider()
            else:
                logger.info("Instantiating MockLLMProvider")
                cls._instances[name] = MockLLMProvider()

        return cls._instances[name]
