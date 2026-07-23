import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.issue import Issue
from app.models.repository import Repository
from app.models.saved_search import SavedSearch
from app.repositories.notification import notification_repo

logger = logging.getLogger(__name__)


class NotificationEngineService:
    """Service scanning newly synced repository issues against user saved searches."""

    async def scan_repository_sync(self, db: AsyncSession, repo_id: uuid.UUID) -> int:
        """Scan all issues of repo_id against saved searches for the repo owner."""
        # 1. Fetch Repository owner
        repo_res = await db.execute(select(Repository).where(Repository.id == repo_id))
        repo = repo_res.scalar_one_or_none()
        if not repo or not repo.added_by_id:
            return 0

        # 2. Fetch User Saved Searches
        searches_res = await db.execute(
            select(SavedSearch).where(SavedSearch.user_id == repo.added_by_id)
        )
        saved_searches = searches_res.scalars().all()
        if not saved_searches:
            return 0

        # 3. Fetch Repository Issues
        issues_res = await db.execute(select(Issue).where(Issue.repository_id == repo.id))
        issues = issues_res.scalars().all()

        notifications_created = 0
        for search_obj in saved_searches:
            filters = search_obj.filters_json or {}
            query_term = (search_obj.search_query or "").lower().strip()

            for issue in issues:
                # Check query term match
                if query_term:
                    title_match = query_term in issue.title.lower()
                    body_match = query_term in (issue.body or "").lower()
                    if not (title_match or body_match):
                        continue

                # Check recommendation filter match
                if filters.get("recommendation") and issue.score:
                    rec_filter = str(filters["recommendation"]).lower()
                    if rec_filter != "all" and issue.score.recommendation.lower() != rec_filter:
                        continue

                # Check difficulty filter match
                if filters.get("difficulty") and issue.analysis:
                    diff_filter = str(filters["difficulty"]).lower()
                    if diff_filter != "all" and issue.analysis.difficulty.lower() != diff_filter:
                        continue

                # Check min_score filter match
                if filters.get("min_score") is not None and issue.score:
                    if issue.score.score < float(filters["min_score"]):
                        continue

                # Issue matches saved search! Create deduplicated notification
                notif = await notification_repo.create_notification(
                    db=db,
                    user_id=repo.added_by_id,
                    title=f"New Matching Issue: #{issue.number} in {repo.full_name}",
                    message=(
                        f"Issue '{issue.title}' matched your saved search '{search_obj.name}'."
                    ),
                    type="new_matching_issue",
                    issue_id=issue.id,
                    saved_search_id=search_obj.id,
                )
                if notif:
                    notifications_created += 1

        if notifications_created > 0:
            await db.commit()

        logger.info(
            f"Notification engine scanned repo {repo.full_name}: "
            f"created {notifications_created} notifications."
        )
        return notifications_created


notification_engine_service = NotificationEngineService()
