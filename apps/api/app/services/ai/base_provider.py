from abc import ABC, abstractmethod
from typing import Any

from app.models.issue import Issue


class BaseLLMProvider(ABC):
    """Abstract base class for all IssueRadar LLM Providers."""

    @abstractmethod
    async def analyze_issue(self, issue: Issue) -> dict[str, Any]:
        """Analyze a single issue and return structured JSON dict matching IssueAnalysis schema."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Name of the underlying LLM model."""
        pass
