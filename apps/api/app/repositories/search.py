import math
import uuid
from typing import Any

from sqlalchemy import String, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.analysis import IssueAnalysis
from app.models.issue import Issue, Label
from app.models.repository import Repository
from app.models.score import IssueScore


class IssueSearchRepository:
    """Dynamic, composable SQLAlchemy query builder for advanced issue search & discovery."""

    async def search_issues(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        search: str | None = None,
        repository_id: uuid.UUID | None = None,
        difficulty: str | None = None,
        risk: str | None = None,
        recommendation: str | None = None,
        min_score: float | None = None,
        max_score: float | None = None,
        min_merge_probability: float | None = None,
        max_estimated_time: int | None = None,
        language: str | None = None,
        label: str | None = None,
        sort: str = "score_desc",
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """Execute composable search query with conditional joins, eager loading, and pagination."""
        # 1. Base query scoped to current user's monitored repositories
        base_stmt = (
            select(Issue)
            .join(Repository, Issue.repository_id == Repository.id)
            .where(Repository.added_by_id == user_id)
        )

        # Determine which tables need to be joined
        need_score = (
            min_score is not None
            or max_score is not None
            or (recommendation is not None and recommendation.lower() != "all")
            or sort in ["score_desc", "score_asc"]
        )

        need_analysis = (
            (difficulty is not None and difficulty.lower() != "all")
            or (risk is not None and risk.lower() != "all")
            or min_merge_probability is not None
            or max_estimated_time is not None
            or language is not None
            or sort in ["merge_desc", "merge_asc", "difficulty", "estimated_time"]
        )

        need_label = label is not None and label.strip() != ""

        # Perform conditional joins
        if need_score:
            base_stmt = base_stmt.outerjoin(IssueScore, Issue.id == IssueScore.issue_id)
        if need_analysis:
            base_stmt = base_stmt.outerjoin(IssueAnalysis, Issue.id == IssueAnalysis.issue_id)
        if need_label:
            base_stmt = base_stmt.join(Issue.labels)

        # 2. Apply Filters
        if search and search.strip():
            term = f"%{search.strip()}%"
            base_stmt = base_stmt.where(or_(Issue.title.ilike(term), Issue.body.ilike(term)))

        if repository_id:
            base_stmt = base_stmt.where(Issue.repository_id == repository_id)

        if recommendation and recommendation.lower() != "all":
            base_stmt = base_stmt.where(IssueScore.recommendation.ilike(recommendation))

        if min_score is not None:
            base_stmt = base_stmt.where(IssueScore.score >= min_score)

        if max_score is not None:
            base_stmt = base_stmt.where(IssueScore.score <= max_score)

        if difficulty and difficulty.lower() != "all":
            base_stmt = base_stmt.where(IssueAnalysis.difficulty.ilike(difficulty))

        if risk and risk.lower() != "all":
            base_stmt = base_stmt.where(IssueAnalysis.risk.ilike(risk))

        if min_merge_probability is not None:
            base_stmt = base_stmt.where(IssueAnalysis.merge_probability >= min_merge_probability)

        if max_estimated_time is not None:
            base_stmt = base_stmt.where(IssueAnalysis.estimated_time_minutes <= max_estimated_time)

        if language and language.strip():
            lang_term = f"%{language.strip()}%"
            base_stmt = base_stmt.where(
                or_(
                    Repository.language.ilike(lang_term),
                    func.cast(IssueAnalysis.languages, String).ilike(lang_term),
                )
            )

        if need_label:
            base_stmt = base_stmt.where(Label.name.ilike(f"%{label.strip()}%"))

        # 3. Compute Total Count Query
        subq = base_stmt.subquery()
        count_stmt = select(func.count()).select_from(subq)
        total_res = await db.execute(count_stmt)
        total = total_res.scalar_one() or 0

        # 4. Apply Sorting
        if sort == "score_desc":
            base_stmt = base_stmt.order_by(
                IssueScore.score.desc().nulls_last(), Issue.github_updated_at.desc()
            )
        elif sort == "score_asc":
            base_stmt = base_stmt.order_by(
                IssueScore.score.asc().nulls_last(), Issue.github_updated_at.desc()
            )
        elif sort == "merge_desc":
            base_stmt = base_stmt.order_by(
                IssueAnalysis.merge_probability.desc().nulls_last(), Issue.github_updated_at.desc()
            )
        elif sort == "merge_asc":
            base_stmt = base_stmt.order_by(
                IssueAnalysis.merge_probability.asc().nulls_last(), Issue.github_updated_at.desc()
            )
        elif sort == "difficulty":
            base_stmt = base_stmt.order_by(
                IssueAnalysis.difficulty.asc().nulls_last(), Issue.github_updated_at.desc()
            )
        elif sort == "estimated_time":
            base_stmt = base_stmt.order_by(
                IssueAnalysis.estimated_time_minutes.asc().nulls_last(),
                Issue.github_updated_at.desc(),
            )
        elif sort == "created_asc":
            base_stmt = base_stmt.order_by(Issue.github_created_at.asc())
        elif sort == "created_desc":
            base_stmt = base_stmt.order_by(Issue.github_created_at.desc())
        elif sort == "updated_asc":
            base_stmt = base_stmt.order_by(Issue.github_updated_at.asc())
        else:  # updated_desc / default
            base_stmt = base_stmt.order_by(Issue.github_updated_at.desc())

        # 5. Apply Pagination and Eager Load Relationships (selectinload prevents N+1 queries)
        safe_page = max(1, page)
        safe_page_size = min(100, max(1, page_size))
        offset = (safe_page - 1) * safe_page_size

        items_stmt = (
            base_stmt.options(
                selectinload(Issue.labels),
                selectinload(Issue.score),
                selectinload(Issue.analysis),
            )
            .offset(offset)
            .limit(safe_page_size)
        )

        items_res = await db.execute(items_stmt)
        # Use unique() when joins produce duplicate rows
        items = items_res.scalars().unique().all()
        pages = math.ceil(total / safe_page_size) if total > 0 else 0

        return {
            "items": items,
            "total": total,
            "page": safe_page,
            "page_size": safe_page_size,
            "pages": pages,
        }


issue_search_repo = IssueSearchRepository()
