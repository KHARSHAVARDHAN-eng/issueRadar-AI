from unittest.mock import patch

from httpx import ASGITransport, AsyncClient
import pytest

from app.models.issue import Issue
from app.models.repository import Repository
from app.services.ai.factory import AIProviderFactory
from app.services.ai.gemini_provider import GeminiProvider
from app.services.ai.mock_provider import MockLLMProvider
from app.services.ai.openai_provider import OpenAIProvider


@pytest.fixture
def sample_issue():
    repo = Repository(
        github_id=123,
        owner="facebook",
        name="react",
        full_name="facebook/react",
        description="React UI library",
        language="JavaScript",
    )
    return Issue(
        number=101,
        title="Fix React component re-render performance bug",
        body="Component re-renders unexpectedly on state update",
        repository=repo,
        comments_count=2,
    )


@pytest.mark.asyncio
async def test_provider_factory_instantiation():
    mock_prov = AIProviderFactory.get_provider("mock")
    assert isinstance(mock_prov, MockLLMProvider)

    gemini_prov = AIProviderFactory.get_provider("gemini")
    assert isinstance(gemini_prov, GeminiProvider)

    openai_prov = AIProviderFactory.get_provider("openai")
    assert isinstance(openai_prov, OpenAIProvider)


@pytest.mark.asyncio
async def test_mock_provider_analysis(sample_issue):
    provider = MockLLMProvider()
    res = await provider.analyze_issue(sample_issue)
    assert res["model_name"] == "mock-gemini-pro-v1"
    assert "problem_explanation" in res
    assert "implementation_plan" in res
    assert len(res["implementation_plan"]) > 0


@pytest.mark.asyncio
async def test_gemini_provider_fallback_without_key(sample_issue):
    provider = GeminiProvider(api_key="")
    res = await provider.analyze_issue(sample_issue)
    assert "summary" in res
    assert "implementation_plan" in res


@pytest.mark.asyncio
async def test_openai_provider_fallback_without_key(sample_issue):
    provider = OpenAIProvider(api_key="")
    res = await provider.analyze_issue(sample_issue)
    assert "summary" in res
    assert "implementation_plan" in res
