import asyncio
import logging
import uuid

from app.core.celery_app import celery_app
from app.core.db import AsyncSessionLocal
from app.repositories.sync_job import sync_job_repo
from app.services.ai.analysis import ai_analysis_service
from app.services.notification_engine import notification_engine_service
from app.services.sync import sync_service

logger = logging.getLogger(__name__)


def _run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as pool:
            return pool.submit(lambda: asyncio.run(coro)).result()
    else:
        return asyncio.run(coro)


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=5,
    name="tasks.sync_repository",
)
def task_sync_repository(
    self,
    repository_id_str: str,
    job_id_str: str | None = None,
    db_session=None,
):
    """Background worker task syncing GitHub repository metadata and issues."""
    logger.info(f"Worker starting task_sync_repository for repo {repository_id_str}")

    async def _run():
        repo_id = uuid.UUID(repository_id_str)
        if db_session:
            if job_id_str:
                job_id = uuid.UUID(job_id_str)
                await sync_job_repo.update_status(db_session, job_id, status="running")
                await db_session.commit()
            return await sync_service.sync_repository(repo_id, db=db_session)

        async with AsyncSessionLocal() as db:
            if job_id_str:
                job_id = uuid.UUID(job_id_str)
                await sync_job_repo.update_status(db, job_id, status="running")
                await db.commit()

            return await sync_service.sync_repository(repo_id, db=db)

    try:
        return _run_async(_run())
    except Exception as exc:
        logger.error(f"Task_sync_repository failed for repo {repository_id_str}: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=5,
    name="tasks.analyze_repository",
)
def task_analyze_repository(self, repository_id_str: str, db_session=None):
    """Background worker task analyzing repository issues with AI."""
    logger.info(f"Worker starting task_analyze_repository for repo {repository_id_str}")

    async def _run():
        repo_id = uuid.UUID(repository_id_str)
        if db_session:
            return await ai_analysis_service.analyze_repository_issues(db_session, repo_id)
        async with AsyncSessionLocal() as db:
            return await ai_analysis_service.analyze_repository_issues(db, repo_id)

    try:
        return _run_async(_run())
    except Exception as exc:
        logger.error(f"Task_analyze_repository failed for repo {repository_id_str}: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=5,
    name="tasks.scan_notifications",
)
def task_scan_notifications(self, repository_id_str: str, db_session=None):
    """Background worker task scanning repository issues against saved searches."""
    logger.info(f"Worker starting task_scan_notifications for repo {repository_id_str}")

    async def _run():
        repo_id = uuid.UUID(repository_id_str)
        if db_session:
            return await notification_engine_service.scan_repository_sync(db_session, repo_id)
        async with AsyncSessionLocal() as db:
            return await notification_engine_service.scan_repository_sync(db, repo_id)

    try:
        return _run_async(_run())
    except Exception as exc:
        logger.error(f"Task_scan_notifications failed for repo {repository_id_str}: {exc}")
        raise self.retry(exc=exc)
