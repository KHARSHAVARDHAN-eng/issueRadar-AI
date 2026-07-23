import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bookmark import Bookmark


class BookmarkRepository:
    """Persistence layer for Bookmark entity."""

    async def create_or_update(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        issue_id: uuid.UUID,
        notes: str | None = None,
    ) -> Bookmark:
        result = await db.execute(
            select(Bookmark).where(Bookmark.user_id == user_id, Bookmark.issue_id == issue_id)
        )
        obj = result.scalar_one_or_none()
        if not obj:
            obj = Bookmark(user_id=user_id, issue_id=issue_id, notes=notes)
            db.add(obj)
        else:
            if notes is not None:
                obj.notes = notes
        await db.flush()
        await db.refresh(obj, ["issue"])
        return obj

    async def get_by_user(self, db: AsyncSession, user_id: uuid.UUID) -> list[Bookmark]:
        result = await db.execute(
            select(Bookmark).where(Bookmark.user_id == user_id).order_by(Bookmark.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_user_and_issue(
        self, db: AsyncSession, user_id: uuid.UUID, issue_id: uuid.UUID
    ) -> Bookmark | None:
        result = await db.execute(
            select(Bookmark).where(Bookmark.user_id == user_id, Bookmark.issue_id == issue_id)
        )
        return result.scalar_one_or_none()

    async def delete(self, db: AsyncSession, obj: Bookmark) -> None:
        await db.delete(obj)
        await db.flush()


bookmark_repo = BookmarkRepository()
