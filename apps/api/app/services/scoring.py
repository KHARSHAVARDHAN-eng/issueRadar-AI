import logging
import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.issue import Issue
from app.models.score import IssueScore
from app.repositories.issue import issue_repo
from app.repositories.score import issue_score_repo

logger = logging.getLogger(__name__)


class IssueScoringService:
    """Deterministic, rule-based scoring engine for open-source issues."""

    def evaluate_issue(self, issue: Issue) -> tuple[float, str, dict[str, float]]:
        """Evaluate single issue against rule factors and return breakdown."""
        breakdown: dict[str, float] = {}

        # 1. Label Analysis
        label_names = [lbl.name.lower() for lbl in issue.labels] if issue.labels else []

        if any(
            gfi in name
            for name in label_names
            for gfi in ["good first issue", "good-first-issue", "help wanted", "easy", "beginner"]
        ):
            breakdown["good_first_issue"] = 25.0

        if any(bug in name for name in label_names for bug in ["bug", "fix", "defect", "error"]):
            breakdown["bug_label"] = 15.0

        if any(
            sec in name
            for name in label_names
            for sec in ["security", "critical", "high priority", "p0", "p1"]
        ):
            breakdown["security_critical"] = 10.0

        if any(feat in name for name in label_names for feat in ["feature", "enhancement"]):
            breakdown["feature_enhancement"] = 5.0

        # 2. Unassigned status (+20 pts)
        # Note: All synced issues currently default to unassigned unless assigned users are tracked
        breakdown["unassigned"] = 20.0

        # 3. Description Analysis
        body = issue.body or ""
        body_lower = body.lower()

        if any(
            kw in body_lower
            for kw in [
                "reproduce",
                "reproduction",
                "steps to reproduce",
                "expected behavior",
                "```",
            ]
        ):
            breakdown["has_reproduction_steps"] = 10.0

        if len(body) > 200:
            breakdown["description_quality"] = 10.0

        # 4. State & PR Penalties
        if issue.state == "closed":
            breakdown["state_closed"] = -50.0

        if issue.is_pull_request:
            breakdown["is_pull_request"] = -30.0

        # 5. Comment Discussion Noise Penalty
        if issue.comments_count > 10:
            extra_comments = issue.comments_count - 10
            noise_penalty = min(20.0, (extra_comments // 5 + 1) * 5.0)
            breakdown["discussion_noise"] = -float(noise_penalty)

        # Final Score Calculation
        total_score = max(0.0, sum(breakdown.values()))

        # Classification Thresholds
        if total_score >= 50.0:
            recommendation = "Implement"
        elif total_score >= 20.0:
            recommendation = "Investigate"
        else:
            recommendation = "Skip"

        return total_score, recommendation, breakdown

    async def score_issue(self, db: AsyncSession, issue: Issue) -> IssueScore:
        """Calculate and persist score for a single issue."""
        score_val, recommendation, breakdown = self.evaluate_issue(issue)
        return await issue_score_repo.upsert_score(
            db=db,
            issue_id=issue.id,
            score_val=score_val,
            recommendation=recommendation,
            breakdown=breakdown,
        )

    async def score_repository_issues(self, db: AsyncSession, repo_id: uuid.UUID) -> int:
        """Score or rescore all issues in a repository and return count of scored issues."""
        issues = await issue_repo.get_by_repository(db, repo_id, state="all")
        count = 0
        for issue in issues:
            await self.score_issue(db, issue)
            count += 1
        await db.commit()
        logger.info(f"Rescored {count} issues for repository {repo_id}.")
        return count

    async def get_ranked_issues(
        self,
        db: AsyncSession,
        repo_id: uuid.UUID,
        recommendation: str | None = None,
        search: str | None = None,
    ) -> Sequence[Issue]:
        """Fetch issues for repository sorted by IssueScore descending."""
        stmt = (
            select(Issue)
            .outerjoin(IssueScore, Issue.id == IssueScore.issue_id)
            .where(Issue.repository_id == repo_id)
        )

        if recommendation and recommendation.lower() != "all":
            stmt = stmt.where(IssueScore.recommendation.ilike(recommendation))
        if search:
            stmt = stmt.where(Issue.title.ilike(f"%{search}%"))

        stmt = stmt.order_by(IssueScore.score.desc().nulls_last(), Issue.github_updated_at.desc())
        result = await db.execute(stmt)
        return result.scalars().all()


scoring_service = IssueScoringService()
