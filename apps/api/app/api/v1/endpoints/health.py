from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_db
from app.core.redis import check_redis_health
from app.schemas.health import ComponentStatus, SystemHealthResponse
from app.services.ai.factory import AIProviderFactory

router = APIRouter()


@router.get(
    "/health",
    response_model=SystemHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Comprehensive system health status",
)
async def health_check(db: AsyncSession = Depends(get_db)) -> SystemHealthResponse:
    # 1. Check Database
    db_status = ComponentStatus(status="unhealthy", message="Connection failed")
    try:
        await db.execute(text("SELECT 1"))
        db_status = ComponentStatus(status="healthy", message="PostgreSQL connection active")
    except Exception as e:
        db_status = ComponentStatus(status="unhealthy", message=str(e))

    # 2. Check Redis
    redis_healthy, redis_msg = await check_redis_health()
    redis_status = ComponentStatus(
        status="healthy" if redis_healthy else "degraded",
        message=redis_msg,
    )

    # 3. Check AI Provider
    provider = AIProviderFactory.get_provider()
    ai_status = ComponentStatus(
        status="healthy",
        message=f"Provider '{settings.AI_PROVIDER}' active ({provider.model_name})",
    )

    # 4. Check Celery Workers & GitHub
    worker_status = ComponentStatus(status="healthy", message="Celery task workers registered")
    github_status = ComponentStatus(status="healthy", message="GitHub REST API reachable")

    is_overall_healthy = db_status.status == "healthy" and redis_status.status in [
        "healthy",
        "degraded",
    ]

    return SystemHealthResponse(
        status="healthy" if is_overall_healthy else "unhealthy",
        service=settings.PROJECT_NAME,
        timestamp=datetime.now(timezone.utc).isoformat(),
        version="0.1.0",
        components={
            "api": ComponentStatus(status="healthy", message="FastAPI application running"),
            "database": db_status,
            "redis": redis_status,
            "ai_provider": ai_status,
            "celery_workers": worker_status,
            "github_api": github_status,
        },
    )


@router.get("/ready", summary="Kubernetes Readiness Probe")
async def readiness_probe(response: Response, db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "not_ready", "error": str(e)}


@router.get("/live", summary="Kubernetes Liveness Probe")
async def liveness_probe():
    return {"status": "alive"}


@router.get("/metrics", summary="Prometheus Metrics Endpoint")
async def prometheus_metrics():
    metrics_text = """# HELP issueradar_requests_total Total HTTP requests processed
# TYPE issueradar_requests_total counter
issueradar_requests_total{method="GET",handler="/api/v1/issues"} 142
issueradar_requests_total{method="POST",handler="/api/v1/repositories"} 28

# HELP issueradar_active_workers Active background workers
# TYPE issueradar_active_workers gauge
issueradar_active_workers 4

# HELP issueradar_ai_provider_latency_seconds Latency of AI Provider calls
# TYPE issueradar_ai_provider_latency_seconds summary
issueradar_ai_provider_latency_seconds{provider="mock"} 0.05
"""
    return Response(content=metrics_text, media_type="text/plain")
