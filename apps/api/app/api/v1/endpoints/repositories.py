import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models.user import User
from app.repositories.issue import issue_repo
from app.repositories.repository import repository_repo
from app.repositories.sync_job import sync_job_repo
from app.schemas.issue import IssueRead
from app.schemas.repository import RepositoryCreate, RepositoryRead
from app.services.ai.analysis import ai_analysis_service
from app.services.repository import repository_service
from app.services.scoring import scoring_service
from app.services.sync import sync_service

router = APIRouter()


@router.post(
    "",
    response_model=RepositoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add GitHub repository",
)
async def add_repository(
    data: RepositoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Validate repository with GitHub REST API and add to user's monitor list."""
    return await repository_service.add_repository(db, current_user, data.url_or_name)


@router.get(
    "",
    response_model=list[RepositoryRead],
    summary="List monitored repositories",
)
async def list_repositories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve all GitHub repositories monitored by current user."""
    return await repository_service.list_repositories(db, current_user)


@router.get(
    "/{repository_id}",
    response_model=RepositoryRead,
    summary="Get repository by ID",
)
async def get_repository(
    repository_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve details for a specific repository."""
    return await repository_service.get_repository(db, current_user, repository_id)


@router.delete(
    "/{repository_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete repository from monitoring",
)
async def delete_repository(
    repository_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a repository from current user's monitor list."""
    await repository_service.delete_repository(db, current_user, repository_id)
    return {"message": "Repository removed successfully"}


@router.post(
    "/{id}/sync",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger background repository synchronization pipeline",
)
async def sync_repository_endpoint(
    id: uuid.UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = await repository_repo.get_by_id(db, id)
    if not repo or repo.added_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found",
        )

    # Create SyncJob record immediately
    job = await sync_job_repo.create_job(db, repo.id)
    await db.commit()

    # Enqueue worker background task
    background_tasks.add_task(sync_service.sync_repository, repo.id, db)

    return {
        "message": f"Synchronization pipeline enqueued for '{repo.full_name}'",
        "job_id": str(job.id),
        "status": "queued",
        "repository_id": str(repo.id),
    }


@router.get(
    "/{repository_id}/issues",
    response_model=list[IssueRead],
    summary="List synchronized repository issues",
)
async def list_repository_issues(
    repository_id: uuid.UUID,
    state: str = Query("all", description="Filter state: 'open', 'closed', or 'all'"),
    search: str | None = Query(None, description="Title search term"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve all synchronized issues for a repository."""
    repo = await repository_service.get_repository(db, current_user, repository_id)
    return await issue_repo.get_by_repository(db, repo.id, state=state, search=search)


@router.post(
    "/{repository_id}/score",
    status_code=status.HTTP_200_OK,
    summary="Rescore all issues for a repository",
)
async def score_repository_issues(
    repository_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Rescore all synchronized issues for a repository using deterministic rules."""
    repo = await repository_service.get_repository(db, current_user, repository_id)
    count = await scoring_service.score_repository_issues(db, repo.id)
    return {
        "message": f"Successfully scored {count} issues for repository {repo.full_name}",
        "scored_count": count,
    }


@router.get(
    "/{repository_id}/ranked-issues",
    response_model=list[IssueRead],
    summary="List repository issues ranked by score descending",
)
async def list_ranked_issues(
    repository_id: uuid.UUID,
    recommendation: str | None = Query(
        None, description="Filter: 'Implement', 'Investigate', 'Skip'"
    ),
    search: str | None = Query(None, description="Title search term"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve repository issues sorted by IssueScore descending."""
    repo = await repository_service.get_repository(db, current_user, repository_id)
    return await scoring_service.get_ranked_issues(
        db, repo.id, recommendation=recommendation, search=search
    )


@router.post(
    "/{repository_id}/analyze",
    status_code=status.HTTP_200_OK,
    summary="Analyze all issues for a repository using AI",
)
async def analyze_repository_issues(
    repository_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger AI analysis for all synchronized issues in a repository."""
    repo = await repository_service.get_repository(db, current_user, repository_id)
    count = await ai_analysis_service.analyze_repository_issues(db, repo.id)
    return {
        "message": f"Successfully analyzed {count} issues with AI for repository {repo.full_name}",
        "analyzed_count": count,
    }
