import pytest
from httpx import ASGITransport, AsyncClient

from app.core.security import create_access_token
from app.main import app
from app.models.repository import Repository
from app.models.user import User
from app.services.sync import sync_service
from tests.conftest import TestAsyncSessionLocal


@pytest.fixture
async def search_user_and_repos():
    async with TestAsyncSessionLocal() as db:
        user = User(
            github_id=123999,
            username="searchuser",
            email="search@test.com",
            avatar_url="https://example.com/avatar.png",
            encrypted_github_token="encrypted_token_search",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        repo1 = Repository(
            github_id=10101,
            owner="facebook",
            name="react",
            full_name="facebook/react",
            description="The React framework",
            language="JavaScript",
            default_branch="main",
            stars=220000,
            forks=45000,
            private=False,
            added_by_id=user.id,
            sync_status="completed",
        )
        db.add(repo1)

        repo2 = Repository(
            github_id=20202,
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
        db.add(repo2)

        await db.commit()
        await db.refresh(repo1)
        await db.refresh(repo2)
        return user, repo1, repo2


@pytest.fixture
def auth_cookie(search_user_and_repos):
    user, _, _ = search_user_and_repos
    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token}


@pytest.mark.asyncio
async def test_search_and_filter_pipeline(search_user_and_repos, auth_cookie):
    _, repo1, repo2 = search_user_and_repos

    # Populate Mock Issues for Repo 1
    mock_issues_1 = [
        {
            "id": 9001,
            "number": 1,
            "title": "Fix React authentication hook memory leak",
            "body": "Steps to reproduce:\n1. Mount component\n2. Log in with JWT",
            "state": "open",
            "html_url": "https://github.com/facebook/react/issues/1",
            "comments": 2,
            "user": {"login": "alice"},
            "created_at": "2026-07-23T10:00:00Z",
            "updated_at": "2026-07-23T12:00:00Z",
            "labels": [
                {"name": "good first issue", "color": "70c24a"},
                {"name": "bug", "color": "d93f0b"},
            ],
        }
    ]

    # Populate Mock Issues for Repo 2
    mock_issues_2 = [
        {
            "id": 9002,
            "number": 2,
            "title": "Complex database query optimization",
            "body": "Refactor architecture for postgres connection pool",
            "state": "open",
            "html_url": "https://github.com/fastapi/fastapi/issues/2",
            "comments": 12,
            "user": {"login": "bob"},
            "created_at": "2026-07-20T10:00:00Z",
            "updated_at": "2026-07-21T12:00:00Z",
            "labels": [{"name": "performance", "color": "0052cc"}],
        }
    ]

    from unittest.mock import patch

    with patch.object(
        sync_service,
        "fetch_github_issues",
        side_effect=[mock_issues_1, mock_issues_2],
    ):
        async with TestAsyncSessionLocal() as db:
            await sync_service.sync_repository(repo1.id, db=db)
            await sync_service.sync_repository(repo2.id, db=db)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Text Search ("authentication")
        resp1 = await client.get("/api/v1/issues?search=authentication", cookies=auth_cookie)
        assert resp1.status_code == 200
        data1 = resp1.json()
        assert data1["total"] == 1
        assert "authentication" in data1["items"][0]["title"].lower()

        # 2. Filter by Difficulty ("beginner")
        resp2 = await client.get("/api/v1/issues?difficulty=beginner", cookies=auth_cookie)
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert data2["total"] == 1
        assert data2["items"][0]["analysis"]["difficulty"] == "beginner"

        # 3. Filter by Recommendation ("Implement")
        resp3 = await client.get("/api/v1/issues?recommendation=Implement", cookies=auth_cookie)
        assert resp3.status_code == 200
        data3 = resp3.json()
        assert data3["total"] >= 1
        assert data3["items"][0]["score"]["recommendation"] == "Implement"

        # 4. Filter by Language ("JavaScript")
        resp4 = await client.get("/api/v1/issues?language=JavaScript", cookies=auth_cookie)
        assert resp4.status_code == 200
        data4 = resp4.json()
        assert data4["total"] == 1

        # 5. Sorting by score_desc
        resp5 = await client.get("/api/v1/issues?sort=score_desc", cookies=auth_cookie)
        assert resp5.status_code == 200
        data5 = resp5.json()
        assert len(data5["items"]) == 2
        assert data5["items"][0]["score"]["score"] >= data5["items"][1]["score"]["score"]

        # 6. Pagination (page=1, page_size=1)
        resp6 = await client.get("/api/v1/issues?page=1&page_size=1", cookies=auth_cookie)
        assert resp6.status_code == 200
        data6 = resp6.json()
        assert data6["page"] == 1
        assert data6["page_size"] == 1
        assert data6["total"] == 2
        assert data6["pages"] == 2
        assert len(data6["items"]) == 1
