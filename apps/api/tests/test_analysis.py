from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.security import create_access_token
from app.main import app
from app.models.repository import Repository
from app.models.user import User
from app.services.ai.analysis import ai_analysis_service
from app.services.ai.mock_provider import MockLLMProvider
from app.services.sync import sync_service
from tests.conftest import TestAsyncSessionLocal


@pytest.fixture
async def ai_user_and_repo():
    async with TestAsyncSessionLocal() as db:
        user = User(
            github_id=666111,
            username="aiuser",
            email="ai@test.com",
            avatar_url="https://example.com/avatar.png",
            encrypted_github_token="encrypted_token_ai",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        repo = Repository(
            github_id=777333,
            owner="fastapi",
            name="fastapi",
            full_name="fastapi/fastapi",
            description="FastAPI framework",
            language="Python",
            default_branch="master",
            stars=70000,
            forks=6000,
            private=False,
            added_by_id=user.id,
            sync_status="completed",
        )
        db.add(repo)
        await db.commit()
        await db.refresh(repo)
        return user, repo


@pytest.fixture
def auth_cookie(ai_user_and_repo):
    user, _ = ai_user_and_repo
    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token}


@pytest.mark.asyncio
async def test_mock_llm_provider_structured_output():
    provider = MockLLMProvider()

    result = await provider.analyze_issue(
        title="Fix authentication cookie expiration bug",
        body="Steps to reproduce:\n1. Log in\n2. Wait 1 hour\nExpected: session refreshed.",
        labels=["good first issue", "bug"],
        comments=["Working on fix"],
    )

    assert result["difficulty"] == "beginner"
    assert result["estimated_time_minutes"] == 30
    assert result["risk"] == "low"
    assert "Authentication Module" in result["component"]
    assert "Python" in result["languages"]
    assert len(result["likely_files"]) > 0
    assert result["merge_probability"] > 0.8
    assert result["model_name"] in ["mock-llm-v1", "mock-gemini-pro-v1"]

    # AI Coach Assertions
    assert "problem_explanation" in result
    assert len(result["implementation_plan"]) > 0
    assert len(result["required_knowledge"]) > 0
    assert len(result["prerequisites"]) > 0
    assert len(result["acceptance_criteria"]) > 0
    assert "testing_strategy" in result
    assert len(result["possible_challenges"]) > 0
    assert result["estimated_learning_time"] > 0
    assert "confidence_reasoning" in result


@pytest.mark.asyncio
async def test_ai_analysis_service_retries_and_persistence(ai_user_and_repo):
    _, repo = ai_user_and_repo

    mock_issues = [
        {
            "id": 8001,
            "number": 201,
            "title": "Database connection pool timeout",
            "body": "Queries timing out under load",
            "state": "open",
            "html_url": "https://github.com/fastapi/fastapi/issues/201",
            "comments": 0,
            "user": {"login": "dev1"},
            "created_at": "2026-07-23T10:00:00Z",
            "updated_at": "2026-07-23T12:00:00Z",
            "labels": [{"name": "bug", "color": "d93f0b"}],
        }
    ]

    with patch.object(sync_service, "fetch_github_issues", return_value=mock_issues):
        async with TestAsyncSessionLocal() as db:
            await sync_service.sync_repository(repo.id, db=db)

    # Verify provider retry handling
    failing_provider = AsyncMock()
    failing_provider.analyze_issue.side_effect = [
        RuntimeError("Transient API timeout"),
        {
            "summary": "Database connection pool fix",
            "difficulty": "intermediate",
            "estimated_time_minutes": 60,
            "risk": "medium",
            "component": "Database Layer",
            "languages": ["Python"],
            "likely_files": ["app/core/db.py"],
            "merge_probability": 0.85,
            "ai_confidence": 0.9,
            "model_name": "test-llm",
            "analysis_version": "1.0",
            "problem_explanation": "Connection pool timeout fix",
            "implementation_plan": ["Step 1", "Step 2"],
            "required_knowledge": ["SQLAlchemy"],
            "prerequisites": ["Run postgres"],
            "acceptance_criteria": ["No timeouts under load"],
            "testing_strategy": "Run load test",
            "possible_challenges": ["High concurrency locks"],
            "estimated_learning_time": 20,
            "confidence_reasoning": "High confidence",
        },
    ]

    with patch.object(ai_analysis_service, "provider", failing_provider):
        async with TestAsyncSessionLocal() as db:
            count = await ai_analysis_service.analyze_repository_issues(db, repo.id)
            assert count == 1
            assert failing_provider.analyze_issue.call_count == 2


@pytest.mark.asyncio
async def test_analyze_repository_issues_and_endpoints(ai_user_and_repo, auth_cookie):
    _, repo = ai_user_and_repo

    mock_issues = [
        {
            "id": 8002,
            "number": 202,
            "title": "UI alignment error",
            "body": "Fix button margins in dark mode",
            "state": "open",
            "html_url": "https://github.com/fastapi/fastapi/issues/202",
            "comments": 0,
            "user": {"login": "dev2"},
            "created_at": "2026-07-23T10:00:00Z",
            "updated_at": "2026-07-23T12:00:00Z",
            "labels": [{"name": "ui", "color": "1d76db"}],
        }
    ]

    with patch.object(sync_service, "fetch_github_issues", return_value=mock_issues):
        async with TestAsyncSessionLocal() as db:
            await sync_service.sync_repository(repo.id, db=db)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. POST /api/v1/repositories/{id}/analyze
        analyze_resp = await client.post(
            f"/api/v1/repositories/{repo.id}/analyze",
            cookies=auth_cookie,
        )
        assert analyze_resp.status_code == 200
        assert analyze_resp.json()["analyzed_count"] == 1

        # Get issue ID
        issues_resp = await client.get(
            f"/api/v1/repositories/{repo.id}/issues",
            cookies=auth_cookie,
        )
        issue_id = issues_resp.json()[0]["id"]

        # 2. GET /api/v1/issues/{id}/analysis
        analysis_resp = await client.get(
            f"/api/v1/issues/{issue_id}/analysis",
            cookies=auth_cookie,
        )
        assert analysis_resp.status_code == 200
        data = analysis_resp.json()
        assert data["issue_id"] == issue_id
        assert data["model_name"] in ["mock-llm-v1", "mock-gemini-pro-v1"]
        assert "problem_explanation" in data
        assert len(data["implementation_plan"]) > 0
        assert len(data["acceptance_criteria"]) > 0
        assert data["estimated_learning_time"] > 0
