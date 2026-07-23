import logging
import uuid
from datetime import datetime, timezone

import httpx
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import AsyncSessionLocal
from app.core.security import decrypt_token
from app.repositories.issue import issue_repo
from app.repositories.repository import repository_repo
from app.repositories.sync_job import sync_job_repo
from app.services.ai.analysis import ai_analysis_service
from app.services.notification_engine import notification_engine_service
from app.services.scoring import scoring_service

logger = logging.getLogger(__name__)


def parse_iso_datetime(date_str: str | None) -> datetime | None:
    """Parse ISO date strings returned by GitHub API."""
    if not date_str:
        return None
    try:
        clean_str = date_str.replace("Z", "+00:00")
        return datetime.fromisoformat(clean_str)
    except Exception as e:
        logger.warning(f"Failed to parse GitHub ISO date '{date_str}': {e}")
        return datetime.now(timezone.utc)


class GitHubSyncService:
    """Service layer responsible for GitHub repository synchronization."""

    async def fetch_github_issues(self, owner: str, name: str, github_token: str) -> list[dict]:
        """Fetch repository issues from official GitHub REST API."""
        headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if github_token:
            headers["Authorization"] = f"Bearer {github_token}"

        url = f"https://api.github.com/repos/{owner}/{name}/issues?state=all&per_page=100"

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"GitHub API sync error ({response.status_code}): {response.text}",
                )
            return response.json()

    async def fetch_issue_comments(
        self, owner: str, name: str, number: int, github_token: str
    ) -> list[dict]:
        """Fetch comments for a specific GitHub issue."""
        headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if github_token:
            headers["Authorization"] = f"Bearer {github_token}"

        url = f"https://api.github.com/repos/{owner}/{name}/issues/{number}/comments"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                return []
            return response.json()

    async def _execute_sync(self, db: AsyncSession, repository_id: uuid.UUID) -> None:
        """Internal execution logic for synchronizing repository metadata and issues."""
        repo = await repository_repo.get_by_id(db, repository_id)
        if not repo:
            logger.error(f"Sync failed: Repository {repository_id} not found.")
            return

        user = repo.added_by
        github_token = decrypt_token(user.encrypted_github_token) if user else ""

        # Create SyncJob entry
        job = await sync_job_repo.create_job(db, repository_id)
        job_id = job.id

        now = datetime.now(timezone.utc)
        repo.sync_status = "in_progress"
        repo.last_sync_started_at = now
        repo.sync_error = None
        await db.commit()

        # Update SyncJob to running
        await sync_job_repo.update_status(db, job_id, status="running")

        try:
            raw_issues = await self.fetch_github_issues(repo.owner, repo.name, github_token)

            synced_issues = []
            for item in raw_issues:
                github_id = item.get("id")
                number = item.get("number")
                title = item.get("title")
                if not github_id or not number or not title:
                    continue

                is_pr = "pull_request" in item
                body = item.get("body")
                state = item.get("state", "open")
                html_url = item.get("html_url", "")
                comments_count = item.get("comments", 0)

                user_info = item.get("user") or {}
                author_username = user_info.get("login")
                author_avatar_url = user_info.get("avatar_url")

                created_at = parse_iso_datetime(item.get("created_at")) or datetime.now(
                    timezone.utc
                )
                updated_at = parse_iso_datetime(item.get("updated_at")) or datetime.now(
                    timezone.utc
                )
                closed_at = parse_iso_datetime(item.get("closed_at"))

                # Process labels
                label_models = []
                raw_labels = item.get("labels") or []
                for lbl in raw_labels:
                    if isinstance(lbl, dict):
                        l_name = lbl.get("name")
                        l_color = lbl.get("color", "888888")
                        l_desc = lbl.get("description")
                        if l_name:
                            label_obj = await issue_repo.get_or_create_label(
                                db, repo.id, l_name, l_color, l_desc
                            )
                            label_models.append(label_obj)

                # Upsert Issue
                issue_obj = await issue_repo.upsert_issue(
                    db=db,
                    repo_id=repo.id,
                    github_id=github_id,
                    number=number,
                    title=title,
                    body=body,
                    state=state,
                    author_username=author_username,
                    author_avatar_url=author_avatar_url,
                    html_url=html_url,
                    comments_count=comments_count,
                    is_pull_request=is_pr,
                    github_created_at=created_at,
                    github_updated_at=updated_at,
                    github_closed_at=closed_at,
                    labels=label_models,
                )

                # Sync Comments if any
                if comments_count > 0:
                    raw_comments = await self.fetch_issue_comments(
                        repo.owner, repo.name, number, github_token
                    )
                    for c_item in raw_comments:
                        c_github_id = c_item.get("id")
                        c_body = c_item.get("body")
                        c_user = c_item.get("user") or {}
                        c_author = c_user.get("login")
                        c_avatar = c_user.get("avatar_url")
                        c_created = parse_iso_datetime(c_item.get("created_at")) or datetime.now(
                            timezone.utc
                        )

                        if c_github_id and c_body:
                            await issue_repo.upsert_comment(
                                db=db,
                                issue_id=issue_obj.id,
                                github_id=c_github_id,
                                body=c_body,
                                author_username=c_author,
                                author_avatar_url=c_avatar,
                                github_created_at=c_created,
                            )

                synced_issues.append(issue_obj)

            # Update Repository counters & sync state
            open_cnt = len([i for i in synced_issues if i.state == "open"])
            closed_cnt = len([i for i in synced_issues if i.state == "closed"])
            total_cnt = len(synced_issues)

            repo.open_issues_count = open_cnt
            repo.closed_issues_count = closed_cnt
            repo.total_issues_count = total_cnt
            repo.sync_status = "completed"
            repo.last_sync_completed_at = datetime.now(timezone.utc)
            repo.sync_error = None
            await db.commit()

            # Automatic rule-based scoring after synchronization
            try:
                await scoring_service.score_repository_issues(db, repo.id)
            except Exception as score_err:
                logger.warning(f"Automatic scoring failed for repo {repo.full_name}: {score_err}")

            # Automatic AI analysis after scoring
            try:
                await ai_analysis_service.analyze_repository_issues(db, repo.id)
            except Exception as ai_err:
                logger.warning(f"Automatic AI analysis failed for repo {repo.full_name}: {ai_err}")

            # Automatic Notification scan against saved searches
            try:
                await notification_engine_service.scan_repository_sync(db, repo.id)
            except Exception as notif_err:
                logger.warning(f"Notification scan failed for repo {repo.full_name}: {notif_err}")

            # Update SyncJob status to completed
            await sync_job_repo.update_status(
                db, job_id, status="completed", issues_processed=total_cnt
            )
            await db.commit()

            logger.info(
                f"Successfully synced, scored, and analyzed repo {repo.full_name}: "
                f"{total_cnt} issues."
            )

        except Exception as e:
            # Update SyncJob status to failed
            await sync_job_repo.update_status(db, job_id, status="failed", errors=str(e))
            logger.error(f"Sync error for repository {repo.full_name}: {e}")
            await db.rollback()
            repo_fail = await repository_repo.get_by_id(db, repository_id)
            if repo_fail:
                repo_fail.sync_status = "failed"
                repo_fail.sync_error = str(e)
                await db.commit()

    async def sync_repository(
        self, repository_id: uuid.UUID, db: AsyncSession | None = None
    ) -> None:
        """Asynchronous entry point for repo synchronization."""
        if db is not None:
            await self._execute_sync(db, repository_id)
        else:
            async with AsyncSessionLocal() as session:
                await self._execute_sync(session, repository_id)


sync_service = GitHubSyncService()
