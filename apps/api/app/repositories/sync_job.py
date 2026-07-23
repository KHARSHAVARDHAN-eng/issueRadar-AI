import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sync_job import SyncJob


class SyncJobRepository:
    """Persistence layer for SyncJob entity."""

    async def create_job(self, db: AsyncSession, repository_id: uuid.UUID) -> SyncJob:
        obj = SyncJob(repository_id=repository_id, status="queued")
        db.add(obj)
        await db.flush()
        return obj

    async def update_status(
        self,
        db: AsyncSession,
        job_id: uuid.UUID,
        status: str,
        issues_processed: int = 0,
        errors: str | None = None,
    ) -> SyncJob | None:
        result = await db.execute(select(SyncJob).where(SyncJob.id == job_id))
        obj = result.scalar_one_or_none()
        if obj:
            now = datetime.now(timezone.utc)
            obj.status = status
            if status == "running" and not obj.started_at:
                obj.started_at = now
            elif status in ["completed", "failed"]:
                obj.finished_at = now
                obj.issues_processed = issues_processed
                if errors:
                    obj.errors = errors
            obj.updated_at = now
            await db.flush()
        return obj

    async def get_by_id(self, db: AsyncSession, job_id: uuid.UUID) -> SyncJob | None:
        result = await db.execute(select(SyncJob).where(SyncJob.id == job_id))
        return result.scalar_one_or_none()

    async def get_recent_jobs(self, db: AsyncSession, limit: int = 20) -> list[SyncJob]:
        result = await db.execute(select(SyncJob).order_by(SyncJob.created_at.desc()).limit(limit))
        return list(result.scalars().all())


sync_job_repo = SyncJobRepository()
