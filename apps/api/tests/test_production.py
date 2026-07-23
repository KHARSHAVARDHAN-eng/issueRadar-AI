import pytest
from httpx import ASGITransport, AsyncClient

from app.core.cache import cache_service
from app.core.security import create_access_token, create_refresh_token
from app.main import app
from app.models.user import User
from tests.conftest import TestAsyncSessionLocal


@pytest.fixture
async def prod_user():
    async with TestAsyncSessionLocal() as db:
        user = User(
            github_id=999222,
            username="produser",
            email="prod@test.com",
            avatar_url="https://example.com/avatar.png",
            encrypted_github_token="encrypted_token_prod",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user


@pytest.fixture
def auth_cookie(prod_user):
    token = create_access_token(data={"sub": str(prod_user.id)})
    return {"access_token": token}


@pytest.mark.asyncio
async def test_cache_service_operations():
    await cache_service.set_json("test_key", {"foo": "bar"}, ttl_seconds=60)
    res = await cache_service.get_json("test_key")
    assert res == {"foo": "bar"}

    count = await cache_service.invalidate_pattern("test_*")
    assert count >= 1
    assert await cache_service.get_json("test_key") is None


@pytest.mark.asyncio
async def test_health_ready_live_metrics_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # GET /health
        h_res = await client.get("/health")
        assert h_res.status_code == 200
        assert h_res.json()["status"] == "healthy"

        # GET /ready
        r_res = await client.get("/ready")
        assert r_res.status_code == 200
        assert r_res.json()["status"] == "ready"

        # GET /live
        l_res = await client.get("/live")
        assert l_res.status_code == 200
        assert l_res.json()["status"] == "alive"

        # GET /metrics
        m_res = await client.get("/metrics")
        assert m_res.status_code == 200
        assert "issueradar_requests_total" in m_res.text


@pytest.mark.asyncio
async def test_refresh_token_rotation_flow(prod_user):
    refresh_token = create_refresh_token(data={"sub": str(prod_user.id)})

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post(
            "/api/v1/auth/refresh",
            cookies={"refresh_token": refresh_token},
        )
        assert res.status_code == 200
        assert "access_token" in res.json()
        assert "access_token" in res.cookies
        assert "refresh_token" in res.cookies


@pytest.mark.asyncio
async def test_rate_limiter_headers():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/")
        assert res.status_code == 200
        assert "X-RateLimit-Limit" in res.headers
        assert "X-RateLimit-Remaining" in res.headers
        assert "X-RateLimit-Reset" in res.headers
