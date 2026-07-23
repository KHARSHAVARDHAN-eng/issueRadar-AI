from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient, Response
from sqlalchemy import select

from app.core.security import create_access_token, decrypt_token
from app.main import app
from app.models.user import User
from tests.conftest import TestAsyncSessionLocal


@pytest.mark.asyncio
async def test_auth_login_redirect():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/auth/login", follow_redirects=False)
        assert response.status_code in (302, 307)
        location = response.headers.get("location")
        assert location is not None
        assert "github.com/login/oauth/authorize" in location
        assert "mock_github_client_id" in location


@pytest.mark.asyncio
async def test_auth_me_unauthenticated():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401
        assert response.json()["detail"] == "Authentication required"


@pytest.mark.asyncio
async def test_auth_callback_and_me_flow():
    mock_client_instance = AsyncMock()

    async def mock_post(url, **kwargs):
        return Response(200, json={"access_token": "gho_mock_github_access_token_123"})

    async def mock_get(url, **kwargs):
        if "user/emails" in str(url):
            return Response(
                200,
                json=[{"email": "octocat@github.com", "primary": True, "verified": True}],
            )
        return Response(
            200,
            json={
                "id": 987654321,
                "login": "octocat",
                "avatar_url": "https://avatars.githubusercontent.com/u/987654321",
                "email": "octocat@github.com",
            },
        )

    mock_client_instance.post.side_effect = mock_post
    mock_client_instance.get.side_effect = mock_get
    mock_client_instance.__aenter__.return_value = mock_client_instance

    with patch(
        "app.api.v1.endpoints.auth.httpx.AsyncClient",
        return_value=mock_client_instance,
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            callback_resp = await client.get(
                "/api/v1/auth/callback?code=valid_oauth_code",
                follow_redirects=False,
            )

            assert callback_resp.status_code == 302
            assert callback_resp.headers["location"] == "http://localhost:3000/dashboard"

            # Verify HttpOnly session cookie set
            assert "access_token" in callback_resp.cookies
            jwt_cookie = callback_resp.cookies["access_token"]

            # Test /me endpoint with session cookie
            me_resp = await client.get("/api/v1/auth/me", cookies={"access_token": jwt_cookie})
            assert me_resp.status_code == 200
            user_data = me_resp.json()
            assert user_data["username"] == "octocat"
            assert user_data["email"] == "octocat@github.com"
            assert user_data["github_id"] == 987654321

            # Verify token encryption in database
            async with TestAsyncSessionLocal() as db:
                db_result = await db.execute(select(User).where(User.github_id == 987654321))
                db_user = db_result.scalar_one()
                assert db_user.encrypted_github_token != "gho_mock_github_access_token_123"
                decrypted = decrypt_token(db_user.encrypted_github_token)
                assert decrypted == "gho_mock_github_access_token_123"


@pytest.mark.asyncio
async def test_auth_logout():
    async with TestAsyncSessionLocal() as db:
        test_user = User(
            github_id=12345,
            username="testlogoutuser",
            email="logout@test.com",
            avatar_url="https://example.com/avatar.png",
            encrypted_github_token="encrypted",
        )
        db.add(test_user)
        await db.commit()
        await db.refresh(test_user)
        user_id = test_user.id

    jwt_token = create_access_token(data={"sub": str(user_id)})

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Verify authenticated
        me_resp = await client.get("/api/v1/auth/me", cookies={"access_token": jwt_token})
        assert me_resp.status_code == 200

        # Perform logout
        logout_resp = await client.post("/api/v1/auth/logout")
        assert logout_resp.status_code == 200
        assert logout_resp.json()["message"] == "Logged out successfully"
