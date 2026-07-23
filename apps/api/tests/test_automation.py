from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.security import create_access_token
from app.main import app
from app.models.repository import Repository
from app.models.user import User
from app.services.notification_engine import notification_engine_service
from app.services.sync import sync_service
from tests.conftest import TestAsyncSessionLocal


@pytest.fixture
async def auto_user_and_repo():
    async with TestAsyncSessionLocal() as db:
        user = User(
            github_id=888111,
            username="autouser",
            email="auto@test.com",
            avatar_url="https://example.com/avatar.png",
            encrypted_github_token="encrypted_token_auto",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        repo = Repository(
            github_id=999111,
            owner="django",
            name="django",
            full_name="django/django",
            description="The Django web framework",
            language="Python",
            default_branch="main",
            stars=75000,
            forks=30000,
            private=False,
            added_by_id=user.id,
            sync_status="completed",
        )
        db.add(repo)
        await db.commit()
        await db.refresh(repo)
        return user, repo


@pytest.fixture
def auth_cookie(auto_user_and_repo):
    user, _ = auto_user_and_repo
    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token}


@pytest.mark.asyncio
async def test_saved_searches_crud(auto_user_and_repo, auth_cookie):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. POST /api/v1/saved-searches
        create_res = await client.post(
            "/api/v1/saved-searches",
            json={
                "name": "Beginner Auth Issues",
                "search_query": "auth",
                "filters_json": {"difficulty": "beginner", "min_score": 50},
            },
            cookies=auth_cookie,
        )
        assert create_res.status_code == 201
        search_id = create_res.json()["id"]

        # 2. GET /api/v1/saved-searches
        list_res = await client.get("/api/v1/saved-searches", cookies=auth_cookie)
        assert list_res.status_code == 200
        assert len(list_res.json()) == 1
        assert list_res.json()[0]["name"] == "Beginner Auth Issues"

        # 3. PUT /api/v1/saved-searches/{id}
        update_res = await client.put(
            f"/api/v1/saved-searches/{search_id}",
            json={"name": "Updated Search Name"},
            cookies=auth_cookie,
        )
        assert update_res.status_code == 200
        assert update_res.json()["name"] == "Updated Search Name"

        # 4. DELETE /api/v1/saved-searches/{id}
        del_res = await client.delete(
            f"/api/v1/saved-searches/{search_id}",
            cookies=auth_cookie,
        )
        assert del_res.status_code == 204


@pytest.mark.asyncio
async def test_bookmarks_and_notifications_flow(auto_user_and_repo, auth_cookie):
    _, repo = auto_user_and_repo

    mock_issues = [
        {
            "id": 9901,
            "number": 501,
            "title": "Fix Django authentication session timeout",
            "body": "Auth session cookie expires early",
            "state": "open",
            "html_url": "https://github.com/django/django/issues/501",
            "comments": 1,
            "user": {"login": "dev_auto"},
            "created_at": "2026-07-23T10:00:00Z",
            "updated_at": "2026-07-23T12:00:00Z",
            "labels": [{"name": "good first issue", "color": "70c24a"}],
        }
    ]

    with patch.object(sync_service, "fetch_github_issues", return_value=mock_issues):
        async with TestAsyncSessionLocal() as db:
            await sync_service.sync_repository(repo.id, db=db)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Get Issue ID
        issues_res = await client.get(f"/api/v1/repositories/{repo.id}/issues", cookies=auth_cookie)
        issue_id = issues_res.json()[0]["id"]

        # 1. Create Saved Search
        await client.post(
            "/api/v1/saved-searches",
            json={
                "name": "Auth Tracker",
                "search_query": "authentication",
                "filters_json": {},
            },
            cookies=auth_cookie,
        )

        # 2. Trigger notification scan
        async with TestAsyncSessionLocal() as db:
            count = await notification_engine_service.scan_repository_sync(db, repo.id)
            assert count == 1

        # 3. GET /api/v1/notifications
        notif_res = await client.get("/api/v1/notifications", cookies=auth_cookie)
        assert notif_res.status_code == 200
        notifs = notif_res.json()
        assert len(notifs) >= 1
        notif_id = notifs[0]["id"]

        # 4. PUT /api/v1/notifications/{id}/read
        read_res = await client.put(f"/api/v1/notifications/{notif_id}/read", cookies=auth_cookie)
        assert read_res.status_code == 200
        assert read_res.json()["is_read"] is True

        # 5. Bookmark issue POST /api/v1/bookmarks
        bm_res = await client.post(
            "/api/v1/bookmarks",
            json={"issue_id": issue_id, "notes": "Important auth issue to work on"},
            cookies=auth_cookie,
        )
        assert bm_res.status_code == 201

        # 6. GET /api/v1/bookmarks
        bm_list = await client.get("/api/v1/bookmarks", cookies=auth_cookie)
        assert bm_list.status_code == 200
        assert len(bm_list.json()) == 1

        # 7. GET /api/v1/jobs
        jobs_res = await client.get("/api/v1/jobs", cookies=auth_cookie)
        assert jobs_res.status_code == 200
        jobs = jobs_res.json()
        assert len(jobs) >= 1
        assert jobs[0]["status"] == "completed"

        # 8. POST /api/v1/jobs/{id}/retry
        retry_res = await client.post(f"/api/v1/jobs/{jobs[0]['id']}/retry", cookies=auth_cookie)
        assert retry_res.status_code == 202
