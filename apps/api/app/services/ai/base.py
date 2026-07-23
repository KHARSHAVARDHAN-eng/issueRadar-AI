from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    """Abstract interface for LLM providers generating structured issue analysis."""

    @abstractmethod
    async def analyze_issue(
        self, title: str, body: str, labels: list[str], comments: list[str]
    ) -> dict:
        """Analyze issue context and return structured JSON dict matching analysis schema."""
        pass
