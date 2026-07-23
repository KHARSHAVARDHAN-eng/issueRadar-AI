import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.score import IssueScore


class IssueScoreRepository:
    """Persistence layer for IssueScore entity."""

    async def upsert_score(
        self,
        db: AsyncSession,
        issue_id: uuid.UUID,
        score_val: float,
        recommendation: str,
        breakdown: dict,
    ) -> IssueScore:
        """Upsert single issue score record."""
        result = await db.execute(select(IssueScore).where(IssueScore.issue_id == issue_id))
        obj = result.scalar_one_or_none()

        if not obj:
            obj = IssueScore(
                issue_id=issue_id,
                score=score_val,
                recommendation=recommendation,
                rule_breakdown=breakdown,
            )
            db.add(obj)
        else:
            obj.score = score_val
            obj.recommendation = recommendation
            obj.rule_breakdown = breakdown
            obj.updated_at = datetime.now(timezone.utc)

        await db.flush()
        return obj

    async def get_by_issue_id(self, db: AsyncSession, issue_id: uuid.UUID) -> IssueScore | None:
        """Fetch score record by issue ID."""
        result = await db.execute(select(IssueScore).where(IssueScore.issue_id == issue_id))
        return result.scalar_one_or_none()


issue_score_repo = IssueScoreRepository()
