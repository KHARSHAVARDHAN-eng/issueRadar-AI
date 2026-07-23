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


class GeminiProvider(BaseLLMProvider):
    """Google Gemini AI Provider generating structured JSON analysis and coaching."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self._fallback_provider = MockLLMProvider()

    @property
    def model_name(self) -> str:
        return "gemini-1.5-flash"

    async def analyze_issue(self, issue: Issue) -> dict[str, Any]:
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not configured. Falling back to MockLLMProvider.")
            return await self._fallback_provider.analyze_issue(issue)

        prompt = ISSUE_ANALYSIS_PROMPT_TEMPLATE.format(
            number=issue.number,
            repo_name=issue.repository.full_name if issue.repository else "Unknown",
            title=issue.title,
            body=issue.body or "No description provided.",
            labels=", ".join(lbl.name for lbl in issue.labels) if issue.labels else "None",
            comment_count=issue.comments_count or 0,
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json"},
        }

        # Attempt API call with retries
        for attempt in range(1, 4):
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    response = await client.post(url, json=payload)
                    if response.status_code == 200:
                        data = response.json()
                        text_content = (
                            data.get("candidates", [{}])[0]
                            .get("content", {})
                            .get("parts", [{}])[0]
                            .get("text", "")
                        )
                        parsed = json.loads(text_content)
                        parsed["model_name"] = self.model_name
                        parsed["analysis_version"] = "1.0"
                        return parsed
                    elif response.status_code == 429:
                        logger.warning(f"Gemini API rate limit (429) on attempt {attempt}.")
                    else:
                        logger.error(
                            f"Gemini API error status {response.status_code}: {response.text}"
                        )
            except Exception as e:
                logger.warning(f"Gemini API exception on attempt {attempt}: {e}")

        logger.error("Gemini API failed after 3 attempts. Falling back to MockLLMProvider.")
        return await self._fallback_provider.analyze_issue(issue)
