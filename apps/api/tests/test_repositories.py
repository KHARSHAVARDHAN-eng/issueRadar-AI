from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient, Response

from app.core.security import create_access_token
from app.main import app
from app.models.user import User
from tests.conftest import TestAsyncSessionLocal


@pytest.fixture
async def authenticated_user():
    async with TestAsyncSessionLocal() as db:
        user = User(
            github_id=55555,
            username="repoowner",
            email="owner@test.com",
            avatar_url="https://example.com/avatar.png",
            encrypted_github_token="encrypted_token_123",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user


@pytest.fixture
def auth_cookie(authenticated_user):
    token = create_access_token(data={"sub": str(authenticated_user.id)})
    return {"access_token": token}


@pytest.mark.asyncio
async def test_add_repository_success(auth_cookie):
    mock_client_instance = AsyncMock()
    mock_client_instance.get.return_value = Response(
        200,
        json={
            "id": 10203040,
            "name": "react",
            "full_name": "facebook/react",
            "owner": {"login": "facebook"},
            "description": "The library for web and native user interfaces.",
            "language": "JavaScript",
            "default_branch": "main",
            "stargazers_count": 220000,
            "forks_count": 45000,
            "private": False,
        },
    )
    mock_client_instance.__aenter__.return_value = mock_client_instance

    with patch("app.services.repository.httpx.AsyncClient", return_value=mock_client_instance):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/repositories",
                json={"url_or_name": "facebook/react"},
                cookies=auth_cookie,
            )

            assert response.status_code == 201
            data = response.json()
            assert data["full_name"] == "facebook/react"
            assert data["stars"] == 220000
            assert data["language"] == "JavaScript"
            assert "id" in data


@pytest.mark.asyncio
async def test_add_repository_duplicate_prevention(auth_cookie):
    mock_client_instance = AsyncMock()
    mock_client_instance.get.return_value = Response(
        200,
        json={
            "id": 10203040,
            "name": "react",
            "full_name": "facebook/react",
            "owner": {"login": "facebook"},
            "description": "React library",
            "language": "JavaScript",
            "default_branch": "main",
            "stargazers_count": 220000,
            "forks_count": 45000,
            "private": False,
        },
    )
    mock_client_instance.__aenter__.return_value = mock_client_instance

    with patch("app.services.repository.httpx.AsyncClient", return_value=mock_client_instance):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # First add succeeds
            resp1 = await client.post(
                "/api/v1/repositories",
                json={"url_or_name": "facebook/react"},
                cookies=auth_cookie,
            )
            assert resp1.status_code == 201

            # Second add returns 400 Bad Request
            resp2 = await client.post(
                "/api/v1/repositories",
                json={"url_or_name": "facebook/react"},
                cookies=auth_cookie,
            )
            assert resp2.status_code == 400
            assert "already added" in resp2.json()["detail"]


@pytest.mark.asyncio
async def test_add_repository_not_found_on_github(auth_cookie):
    mock_client_instance = AsyncMock()
    mock_client_instance.get.return_value = Response(404, json={"message": "Not Found"})
    mock_client_instance.__aenter__.return_value = mock_client_instance

    with patch("app.services.repository.httpx.AsyncClient", return_value=mock_client_instance):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/repositories",
                json={"url_or_name": "nonexistent/repo12345"},
                cookies=auth_cookie,
            )
            assert response.status_code == 404
            assert "not found on GitHub" in response.json()["detail"]


@pytest.mark.asyncio
async def test_list_and_delete_repository_flow(auth_cookie):
    mock_client_instance = AsyncMock()
    mock_client_instance.get.return_value = Response(
        200,
        json={
            "id": 99988877,
            "name": "fastapi",
            "full_name": "tiangolo/fastapi",
            "owner": {"login": "tiangolo"},
            "description": "FastAPI framework",
            "language": "Python",
            "default_branch": "master",
            "stargazers_count": 70000,
            "forks_count": 6000,
            "private": False,
        },
    )
    mock_client_instance.__aenter__.return_value = mock_client_instance

    with patch("app.services.repository.httpx.AsyncClient", return_value=mock_client_instance):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. Add repository
            add_resp = await client.post(
                "/api/v1/repositories",
                json={"url_or_name": "tiangolo/fastapi"},
                cookies=auth_cookie,
            )
            assert add_resp.status_code == 201
            repo_id = add_resp.json()["id"]

            # 2. List repositories
            list_resp = await client.get("/api/v1/repositories", cookies=auth_cookie)
            assert list_resp.status_code == 200
            repos = list_resp.json()
            assert len(repos) == 1
            assert repos[0]["full_name"] == "tiangolo/fastapi"

            # 3. Get single repository
            get_resp = await client.get(f"/api/v1/repositories/{repo_id}", cookies=auth_cookie)
            assert get_resp.status_code == 200
            assert get_resp.json()["id"] == repo_id

            # 4. Delete repository
            del_resp = await client.delete(f"/api/v1/repositories/{repo_id}", cookies=auth_cookie)
            assert del_resp.status_code == 200

            # 5. Verify list is now empty
            empty_list_resp = await client.get("/api/v1/repositories", cookies=auth_cookie)
            assert empty_list_resp.status_code == 200
            assert len(empty_list_resp.json()) == 0
