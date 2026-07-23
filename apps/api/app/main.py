import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import health as health_endpoint
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import RequestLoggingMiddleware, setup_structured_logging
from app.core.rate_limit import RateLimiterMiddleware
from app.core.redis import close_redis, init_redis

setup_structured_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown procedures."""
    logger.info(
        f"Starting {settings.PROJECT_NAME} API v{settings.VERSION} [{settings.ENVIRONMENT}]"
    )
    await init_redis()
    yield
    await close_redis()
    logger.info("Shutdown completed.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Middlewares
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimiterMiddleware, anon_limit=100, auth_limit=300)

if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include root health check & probes
app.include_router(health_endpoint.router, tags=["Health"])

# Include versioned API router at /api/v1
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "health": "/health",
        "docs": "/docs",
    }
