import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models.user import User
from app.repositories.sync_job import sync_job_repo
from app.schemas.sync_job import SyncJobRead
from app.services.sync import sync_service

router = APIRouter()


@router.get(
    "",
    response_model=list[SyncJobRead],
    summary="List background sync jobs (paginated)",
)
async def list_sync_jobs(
    limit: int = Query(30, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await sync_job_repo.get_recent_jobs(db, limit=limit)


@router.get(
    "/{job_id}",
    summary="Get detailed sync job progress and metrics",
)
async def get_sync_job_detail(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    job = await sync_job_repo.get_by_id(db, job_id)
    if not job or job.repository.added_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sync job not found",
        )

    # Progress calculation
    progress = 100 if job.status == "completed" else (50 if job.status == "running" else 0)

    return {
        "id": str(job.id),
        "repository_id": str(job.repository_id),
        "repository_name": job.repository.full_name,
        "status": job.status,
        "progress": progress,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "finished_at": job.finished_at.isoformat() if job.finished_at else None,
        "processed": job.issues_processed,
        "remaining": 0 if job.status == "completed" else 1,
        "error": job.errors,
        "created_at": job.created_at.isoformat(),
        "updated_at": job.updated_at.isoformat(),
    }


@router.post(
    "/{job_id}/retry",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Retry a failed or completed sync job",
)
async def retry_sync_job(
    job_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    job = await sync_job_repo.get_by_id(db, job_id)
    if not job or job.repository.added_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sync job not found",
        )

    # Trigger background sync for repository
    background_tasks.add_task(sync_service.sync_repository, job.repository_id, db)
    return {
        "message": f"Enqueued retry for sync job {job_id} (Repository: {job.repository.full_name})",
        "job_id": str(job_id),
        "status": "queued",
    }
