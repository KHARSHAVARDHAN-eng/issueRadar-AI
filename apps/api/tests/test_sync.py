from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.security import create_access_token
from app.main import app
from app.models.repository import Repository
from app.models.user import User
from app.services.sync import sync_service
from tests.conftest import TestAsyncSessionLocal


@pytest.fixture
async def sync_user_and_repo():
    async with TestAsyncSessionLocal() as db:
        user = User(
            github_id=88888,
            username="synctestuser",
            email="sync@test.com",
            avatar_url="https://example.com/avatar.png",
            encrypted_github_token="encrypted_token_abc",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        repo = Repository(
            github_id=999000,
            owner="octocat",
            name="Hello-World",
            full_name="octocat/Hello-World",
            description="My first repository",
            language="Python",
            default_branch="main",
            stars=100,
            forks=20,
            private=False,
            added_by_id=user.id,
            sync_status="idle",
        )
        db.add(repo)
        await db.commit()
        await db.refresh(repo)
        return user, repo


@pytest.fixture
def auth_cookie(sync_user_and_repo):
    user, _ = sync_user_and_repo
    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token}


@pytest.mark.asyncio
async def test_post_sync_repository_returns_202(sync_user_and_repo, auth_cookie):
    _, repo = sync_user_and_repo
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        with patch.object(sync_service, "sync_repository", new_callable=AsyncMock):
            response = await client.post(
                f"/api/v1/repositories/{repo.id}/sync",
                cookies=auth_cookie,
            )
            assert response.status_code == 202
            data = response.json()
            assert data["status"] in ["queued", "pending"]
            assert data["repository_id"] == str(repo.id)


@pytest.mark.asyncio
async def test_sync_repository_service_upsert(sync_user_and_repo):
    _, repo = sync_user_and_repo

    mock_issues = [
        {
            "id": 111222,
            "number": 1,
            "title": "Bug in login flow",
            "body": "Fix authentication error",
            "state": "open",
            "html_url": "https://github.com/octocat/Hello-World/issues/1",
            "comments": 1,
            "user": {"login": "alice", "avatar_url": "https://example.com/alice.png"},
            "created_at": "2026-07-23T10:00:00Z",
            "updated_at": "2026-07-23T12:00:00Z",
            "closed_at": None,
            "labels": [{"name": "bug", "color": "f29513", "description": "Bug label"}],
        },
        {
            "id": 333444,
            "number": 2,
            "title": "Documentation update",
            "body": "Update README",
            "state": "closed",
            "html_url": "https://github.com/octocat/Hello-World/issues/2",
            "comments": 0,
            "user": {"login": "bob", "avatar_url": "https://example.com/bob.png"},
            "created_at": "2026-07-20T10:00:00Z",
            "updated_at": "2026-07-21T12:00:00Z",
            "closed_at": "2026-07-21T12:00:00Z",
            "labels": [{"name": "docs", "color": "0075ca"}],
        },
    ]

    mock_comments = [
        {
            "id": 777888,
            "body": "I am working on this bug",
            "user": {"login": "charlie", "avatar_url": "https://example.com/charlie.png"},
            "created_at": "2026-07-23T11:00:00Z",
        }
    ]

    with (
        patch.object(sync_service, "fetch_github_issues", return_value=mock_issues),
        patch.object(sync_service, "fetch_issue_comments", return_value=mock_comments),
    ):
        # 1. Run first sync execution
        async with TestAsyncSessionLocal() as db:
            await sync_service.sync_repository(repo.id, db=db)

        async with TestAsyncSessionLocal() as db:
            updated_repo = await db.get(Repository, repo.id)
            assert updated_repo.sync_status == "completed"
            assert updated_repo.total_issues_count == 2
            assert updated_repo.open_issues_count == 1
            assert updated_repo.closed_issues_count == 1
            assert updated_repo.last_sync_completed_at is not None

        # 2. Run second sync execution to verify upsert duplicate safety
        async with TestAsyncSessionLocal() as db:
            await sync_service.sync_repository(repo.id, db=db)

        async with TestAsyncSessionLocal() as db:
            updated_repo2 = await db.get(Repository, repo.id)
            assert updated_repo2.sync_status == "completed"
            assert updated_repo2.total_issues_count == 2


@pytest.mark.asyncio
async def test_get_repository_issues_and_detail_endpoints(sync_user_and_repo, auth_cookie):
    _, repo = sync_user_and_repo

    mock_issues = [
        {
            "id": 999111,
            "number": 42,
            "title": "Critical performance issue",
            "body": "Slow database queries",
            "state": "open",
            "html_url": "https://github.com/octocat/Hello-World/issues/42",
            "comments": 0,
            "user": {"login": "dev", "avatar_url": "https://example.com/dev.png"},
            "created_at": "2026-07-23T10:00:00Z",
            "updated_at": "2026-07-23T12:00:00Z",
            "labels": [{"name": "performance", "color": "d93f0b"}],
        }
    ]

    with patch.object(sync_service, "fetch_github_issues", return_value=mock_issues):
        async with TestAsyncSessionLocal() as db:
            await sync_service.sync_repository(repo.id, db=db)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. GET /api/v1/repositories/{id}/issues
        issues_resp = await client.get(
            f"/api/v1/repositories/{repo.id}/issues",
            cookies=auth_cookie,
        )
        assert issues_resp.status_code == 200
        issues_data = issues_resp.json()
        assert len(issues_data) == 1
        assert issues_data[0]["number"] == 42
        assert issues_data[0]["labels"][0]["name"] == "performance"
        issue_id = issues_data[0]["id"]

        # 2. GET /api/v1/issues/{id}
        detail_resp = await client.get(
            f"/api/v1/issues/{issue_id}",
            cookies=auth_cookie,
        )
        assert detail_resp.status_code == 200
        detail_data = detail_resp.json()
        assert detail_data["id"] == issue_id
        assert detail_data["title"] == "Critical performance issue"
