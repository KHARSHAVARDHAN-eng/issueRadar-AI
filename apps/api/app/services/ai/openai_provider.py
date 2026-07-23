import json
import logging
from typing import Any

import httpx

from app.core.config import settings
from app.models.issue import Issue
from app.services.ai.base_provider import BaseLLMProvider
from app.services.ai.mock_provider import MockLLMProvider
from app.services.ai.prompts import ISSUE_ANALYSIS_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT-4.1 / GPT-5 compatible AI Provider with structured JSON response mode."""

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self._model = model
        self._fallback_provider = MockLLMProvider()

    @property
    def model_name(self) -> str:
        return self._model

    async def analyze_issue(self, issue: Issue) -> dict[str, Any]:
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not configured. Falling back to MockLLMProvider.")
            return await self._fallback_provider.analyze_issue(issue)

        prompt = ISSUE_ANALYSIS_PROMPT_TEMPLATE.format(
            number=issue.number,
            repo_name=issue.repository.full_name if issue.repository else "Unknown",
            title=issue.title,
            body=issue.body or "No description provided.",
            labels=", ".join(lbl.name for lbl in issue.labels) if issue.labels else "None",
            comment_count=issue.comments_count or 0,
        )

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model_name,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a Lead Open Source Architect producing structured JSON analysis."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        }

        # Attempt API call with retries
        for attempt in range(1, 4):
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    response = await client.post(url, headers=headers, json=payload)
                    if response.status_code == 200:
                        data = response.json()
                        text_content = data["choices"][0]["message"]["content"]
                        parsed = json.loads(text_content)
                        parsed["model_name"] = self.model_name
                        parsed["analysis_version"] = "1.0"
                        return parsed
                    elif response.status_code in [429, 500, 503]:
                        logger.warning(
                            f"OpenAI API status {response.status_code} on attempt {attempt}."
                        )
                    else:
                        logger.error(
                            f"OpenAI API error status {response.status_code}: {response.text}"
                        )
            except Exception as e:
                logger.warning(f"OpenAI API exception on attempt {attempt}: {e}")

        logger.error("OpenAI API failed after 3 attempts. Falling back to MockLLMProvider.")
        return await self._fallback_provider.analyze_issue(issue)
