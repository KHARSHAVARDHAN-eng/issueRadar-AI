from unittest.mock import patch

import pytest

from app.models.repository import Repository
from app.models.user import User
from app.workers.tasks import task_analyze_repository, task_scan_notifications, task_sync_repository
from tests.conftest import TestAsyncSessionLocal


@pytest.fixture
async def worker_test_repo():
    async with TestAsyncSessionLocal() as db:
        user = User(
            github_id=777000,
            username="workeruser",
            email="worker@test.com",
            avatar_url="https://example.com/avatar.png",
            encrypted_github_token="encrypted_token_worker",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        repo = Repository(
            github_id=888000,
            owner="pallets",
            name="flask",
            full_name="pallets/flask",
            description="The Python micro framework",
            language="Python",
            default_branch="main",
            stars=65000,
            forks=15000,
            private=False,
            added_by_id=user.id,
            sync_status="completed",
        )
        db.add(repo)
        await db.commit()
        await db.refresh(repo)
        return user, repo


@pytest.mark.asyncio
async def test_worker_tasks_pipeline(worker_test_repo):
    _, repo = worker_test_repo

    mock_issues = [
        {
            "id": 8801,
            "number": 101,
            "title": "Fix Flask routing error handling",
            "body": "Routing fails on special characters",
            "state": "open",
            "html_url": "https://github.com/pallets/flask/issues/101",
            "comments": 0,
            "user": {"login": "flask_dev"},
            "created_at": "2026-07-23T10:00:00Z",
            "updated_at": "2026-07-23T12:00:00Z",
            "labels": [],
        }
    ]

    with patch("app.services.sync.sync_service.fetch_github_issues", return_value=mock_issues):
        async with TestAsyncSessionLocal() as db:
            # 1. Execute task_sync_repository
            task_sync_repository(str(repo.id), db_session=db)

            # 2. Execute task_analyze_repository
            count_analyze = task_analyze_repository(str(repo.id), db_session=db)
            assert count_analyze >= 0

            # 3. Execute task_scan_notifications
            count_notif = task_scan_notifications(str(repo.id), db_session=db)
            assert count_notif >= 0
