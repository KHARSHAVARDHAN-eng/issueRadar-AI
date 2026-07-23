from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    bookmarks,
    issues,
    jobs,
    notifications,
    repositories,
    saved_searches,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(repositories.router, prefix="/repositories", tags=["repositories"])
api_router.include_router(issues.router, prefix="/issues", tags=["issues"])
api_router.include_router(saved_searches.router, prefix="/saved-searches", tags=["saved-searches"])
api_router.include_router(bookmarks.router, prefix="/bookmarks", tags=["bookmarks"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
