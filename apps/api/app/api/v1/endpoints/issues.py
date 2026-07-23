import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models.user import User
from app.repositories.analysis import issue_analysis_repo
from app.repositories.issue import issue_repo
from app.repositories.score import issue_score_repo
from app.repositories.search import issue_search_repo
from app.schemas.analysis import IssueAnalysisRead
from app.schemas.issue import IssueDetailRead
from app.schemas.score import IssueScoreRead
from app.schemas.search import PaginatedIssuesResponse
from app.services.ai.analysis import ai_analysis_service
from app.services.scoring import scoring_service

router = APIRouter()


@router.get(
    "",
    response_model=PaginatedIssuesResponse,
    summary="Advanced search and discovery across monitored repository issues",
)
async def search_issues(
    search: str | None = Query(None, description="Title and body search string"),
    repository_id: uuid.UUID | None = Query(None, description="Filter by repository ID"),
    difficulty: str | None = Query(
        None, description="Filter: 'beginner', 'intermediate', 'advanced'"
    ),
    risk: str | None = Query(None, description="Filter: 'low', 'medium', 'high'"),
    recommendation: str | None = Query(
        None, description="Filter: 'Implement', 'Investigate', 'Skip'"
    ),
    min_score: float | None = Query(None, description="Minimum numeric rule score"),
    max_score: float | None = Query(None, description="Maximum numeric rule score"),
    min_merge_probability: float | None = Query(
        None, description="Minimum merge probability (0.0 - 1.0)"
    ),
    max_estimated_time: int | None = Query(None, description="Maximum estimated time in minutes"),
    language: str | None = Query(None, description="Filter by programming language"),
    label: str | None = Query(None, description="Filter by issue label name"),
    sort: str = Query(
        "score_desc",
        description="Sort option e.g. 'score_desc', 'merge_desc', 'difficulty', 'created_desc'",
    ),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Perform advanced search and filtering with dynamic composable query building."""
    return await issue_search_repo.search_issues(
        db=db,
        user_id=current_user.id,
        search=search,
        repository_id=repository_id,
        difficulty=difficulty,
        risk=risk,
        recommendation=recommendation,
        min_score=min_score,
        max_score=max_score,
        min_merge_probability=min_merge_probability,
        max_estimated_time=max_estimated_time,
        language=language,
        label=label,
        sort=sort,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{issue_id}",
    response_model=IssueDetailRead,
    summary="Get issue detail by ID",
)
async def get_issue(
    issue_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve detailed information for a specific issue, including comments and labels."""
    issue = await issue_repo.get_by_id(db, issue_id)
    if not issue or issue.repository.added_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found",
        )
    return issue


@router.get(
    "/{issue_id}/score",
    response_model=IssueScoreRead,
    summary="Get issue score and rule breakdown",
)
async def get_issue_score(
    issue_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve deterministic score and explainability rule breakdown for an issue."""
    issue = await issue_repo.get_by_id(db, issue_id)
    if not issue or issue.repository.added_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found",
        )

    score_obj = await issue_score_repo.get_by_issue_id(db, issue_id)
    if not score_obj:
        score_obj = await scoring_service.score_issue(db, issue)
        await db.commit()

    return score_obj


@router.get(
    "/{issue_id}/analysis",
    response_model=IssueAnalysisRead,
    summary="Get issue AI analysis insights",
)
async def get_issue_analysis(
    issue_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve AI-generated insights (summary, difficulty, effort, risk, likely files)."""
    issue = await issue_repo.get_by_id(db, issue_id)
    if not issue or issue.repository.added_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found",
        )

    analysis_obj = await issue_analysis_repo.get_by_issue_id(db, issue_id)
    if not analysis_obj:
        analysis_obj = await ai_analysis_service.analyze_issue(db, issue)
        await db.commit()

    return analysis_obj
