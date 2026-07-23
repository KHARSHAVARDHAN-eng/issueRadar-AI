import uuid
from collections.abc import Sequence
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.issue import Comment, Issue, Label


class IssueRepository:
    """Persistence layer for Issue, Label, and Comment ORM entities with upsert support."""

    async def get_or_create_label(
        self, db: AsyncSession, repo_id: uuid.UUID, name: str, color: str, description: str | None
    ) -> Label:
        result = await db.execute(
            select(Label).where(Label.repository_id == repo_id, Label.name == name)
        )
        label = result.scalar_one_or_none()
        if not label:
            label = Label(
                repository_id=repo_id,
                name=name,
                color=color or "888888",
                description=description,
            )
            db.add(label)
            await db.flush()
        else:
            label.color = color or label.color
            label.description = description or label.description
        return label

    async def upsert_issue(
        self,
        db: AsyncSession,
        repo_id: uuid.UUID,
        github_id: int,
        number: int,
        title: str,
        body: str | None,
        state: str,
        author_username: str | None,
        author_avatar_url: str | None,
        html_url: str,
        comments_count: int,
        is_pull_request: bool,
        github_created_at: datetime,
        github_updated_at: datetime,
        github_closed_at: datetime | None,
        labels: list[Label],
    ) -> Issue:
        """Upsert single issue and link associated labels."""
        result = await db.execute(
            select(Issue).where(
                Issue.repository_id == repo_id,
                Issue.github_id == github_id,
            )
        )
        issue = result.scalar_one_or_none()

        if not issue:
            issue = Issue(
                github_id=github_id,
                number=number,
                title=title,
                body=body,
                state=state,
                author_username=author_username,
                author_avatar_url=author_avatar_url,
                html_url=html_url,
                comments_count=comments_count,
                is_pull_request=is_pull_request,
                repository_id=repo_id,
                github_created_at=github_created_at,
                github_updated_at=github_updated_at,
                github_closed_at=github_closed_at,
            )
            db.add(issue)
        else:
            issue.number = number
            issue.title = title
            issue.body = body
            issue.state = state
            issue.author_username = author_username
            issue.author_avatar_url = author_avatar_url
            issue.html_url = html_url
            issue.comments_count = comments_count
            issue.is_pull_request = is_pull_request
            issue.github_updated_at = github_updated_at
            issue.github_closed_at = github_closed_at
            issue.updated_at = datetime.now(timezone.utc)

        # Associate labels
        issue.labels = labels
        await db.flush()
        return issue

    async def upsert_comment(
        self,
        db: AsyncSession,
        issue_id: uuid.UUID,
        github_id: int,
        body: str,
        author_username: str | None,
        author_avatar_url: str | None,
        github_created_at: datetime,
    ) -> Comment:
        """Upsert a comment for an issue."""
        result = await db.execute(select(Comment).where(Comment.github_id == github_id))
        comment = result.scalar_one_or_none()

        if not comment:
            comment = Comment(
                github_id=github_id,
                issue_id=issue_id,
                body=body,
                author_username=author_username,
                author_avatar_url=author_avatar_url,
                github_created_at=github_created_at,
            )
            db.add(comment)
        else:
            comment.body = body
            comment.author_username = author_username
            comment.author_avatar_url = author_avatar_url

        await db.flush()
        return comment

    async def get_by_repository(
        self,
        db: AsyncSession,
        repo_id: uuid.UUID,
        state: str | None = None,
        search: str | None = None,
    ) -> Sequence[Issue]:
        """Fetch issues for a repository ordered by github_updated_at desc."""
        stmt = select(Issue).where(Issue.repository_id == repo_id)
        if state and state != "all":
            stmt = stmt.where(Issue.state == state)
        if search:
            stmt = stmt.where(Issue.title.ilike(f"%{search}%"))

        stmt = stmt.order_by(Issue.github_updated_at.desc())
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, db: AsyncSession, issue_id: uuid.UUID) -> Issue | None:
        """Fetch single issue by ID with labels and comments loaded."""
        result = await db.execute(select(Issue).where(Issue.id == issue_id))
        return result.scalar_one_or_none()


issue_repo = IssueRepository()
