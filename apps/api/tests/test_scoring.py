from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.security import create_access_token
from app.main import app
from app.models.issue import Issue, Label
from app.models.repository import Repository
from app.models.user import User
from app.services.scoring import scoring_service
from app.services.sync import sync_service
from tests.conftest import TestAsyncSessionLocal


@pytest.fixture
async def scoring_user_and_repo():
    async with TestAsyncSessionLocal() as db:
        user = User(
            github_id=777111,
            username="scoreuser",
            email="score@test.com",
            avatar_url="https://example.com/avatar.png",
            encrypted_github_token="encrypted_token_xyz",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        repo = Repository(
            github_id=888222,
            owner="facebook",
            name="react",
            full_name="facebook/react",
            description="The React library",
            language="JavaScript",
            default_branch="main",
            stars=220000,
            forks=45000,
            private=False,
            added_by_id=user.id,
            sync_status="completed",
        )
        db.add(repo)
        await db.commit()
        await db.refresh(repo)
        return user, repo


@pytest.fixture
def auth_cookie(scoring_user_and_repo):
    user, _ = scoring_user_and_repo
    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token}


def test_evaluate_issue_scoring_rules():
    # 1. High score issue -> Implement
    high_issue = Issue(
        number=1,
        title="Fix memory leak in render loop",
        body=(
            "Steps to reproduce:\n1. Open page\n2. Click button fast\n"
            "Expected behavior: Memory stays constant. ```js code() ```" * 5
        ),
        state="open",
        comments_count=2,
        is_pull_request=False,
        labels=[
            Label(name="good first issue", color="70c24a"),
            Label(name="bug", color="d93f0b"),
        ],
    )
    score, rec, breakdown = scoring_service.evaluate_issue(high_issue)
    assert score >= 50.0
    assert rec == "Implement"
    assert breakdown["good_first_issue"] == 25.0
    assert breakdown["bug_label"] == 15.0
    assert breakdown["has_reproduction_steps"] == 10.0
    assert breakdown["description_quality"] == 10.0

    # 2. Closed PR issue -> Skip
    closed_pr = Issue(
        number=2,
        title="Refactor build script",
        body="Short description",
        state="closed",
        comments_count=15,
        is_pull_request=True,
        labels=[],
    )
    score_pr, rec_pr, breakdown_pr = scoring_service.evaluate_issue(closed_pr)
    assert rec_pr == "Skip"
    assert breakdown_pr.get("state_closed") == -50.0
    assert breakdown_pr.get("is_pull_request") == -30.0


@pytest.mark.asyncio
async def test_score_repository_issues_and_endpoints(scoring_user_and_repo, auth_cookie):
    _, repo = scoring_user_and_repo

    mock_issues = [
        {
            "id": 5001,
            "number": 101,
            "title": "Good first issue bug",
            "body": "Detailed steps to reproduce the error in component rendering...",
            "state": "open",
            "html_url": "https://github.com/facebook/react/issues/101",
            "comments": 1,
            "user": {"login": "dev1"},
            "created_at": "2026-07-23T10:00:00Z",
            "updated_at": "2026-07-23T12:00:00Z",
            "labels": [{"name": "good first issue", "color": "70c24a"}],
        },
        {
            "id": 5002,
            "number": 102,
            "title": "Closed feature request",
            "body": "Feature already implemented",
            "state": "closed",
            "html_url": "https://github.com/facebook/react/issues/102",
            "comments": 2,
            "user": {"login": "dev2"},
            "created_at": "2026-07-20T10:00:00Z",
            "updated_at": "2026-07-21T12:00:00Z",
            "closed_at": "2026-07-21T12:00:00Z",
            "labels": [{"name": "feature", "color": "a2eeef"}],
        },
    ]

    with patch.object(sync_service, "fetch_github_issues", return_value=mock_issues):
        async with TestAsyncSessionLocal() as db:
            await sync_service.sync_repository(repo.id, db=db)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. POST /api/v1/repositories/{id}/score
        rescore_resp = await client.post(
            f"/api/v1/repositories/{repo.id}/score",
            cookies=auth_cookie,
        )
        assert rescore_resp.status_code == 200
        assert rescore_resp.json()["scored_count"] == 2

        # 2. GET /api/v1/repositories/{id}/ranked-issues
        ranked_resp = await client.get(
            f"/api/v1/repositories/{repo.id}/ranked-issues",
            cookies=auth_cookie,
        )
        assert ranked_resp.status_code == 200
        ranked_data = ranked_resp.json()
        assert len(ranked_data) == 2
        # First issue should have higher score than second issue
        assert ranked_data[0]["score"]["score"] > ranked_data[1]["score"]["score"]
        issue_id = ranked_data[0]["id"]

        # 3. GET /api/v1/issues/{id}/score
        score_resp = await client.get(
            f"/api/v1/issues/{issue_id}/score",
            cookies=auth_cookie,
        )
        assert score_resp.status_code == 200
        score_data = score_resp.json()
        assert score_data["issue_id"] == issue_id
        assert "good_first_issue" in score_data["rule_breakdown"]
