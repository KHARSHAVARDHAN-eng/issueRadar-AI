import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification


class NotificationRepository:
    """Persistence layer for Notification entity."""

    async def create_notification(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        title: str,
        message: str,
        type: str = "new_matching_issue",
        issue_id: uuid.UUID | None = None,
        saved_search_id: uuid.UUID | None = None,
    ) -> Notification:
        # Check duplicate
        if issue_id and saved_search_id:
            existing = await db.execute(
                select(Notification).where(
                    Notification.user_id == user_id,
                    Notification.issue_id == issue_id,
                    Notification.saved_search_id == saved_search_id,
                )
            )
            if existing.scalar_one_or_none():
                return existing.scalar_one()

        obj = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=type,
            issue_id=issue_id,
            saved_search_id=saved_search_id,
        )
        db.add(obj)
        await db.flush()
        return obj

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        unread_only: bool = False,
        limit: int = 50,
    ) -> list[Notification]:
        stmt = select(Notification).where(Notification.user_id == user_id)
        if unread_only:
            stmt = stmt.where(Notification.is_read == False)  # noqa: E712
        stmt = stmt.order_by(Notification.created_at.desc()).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def mark_read(
        self, db: AsyncSession, user_id: uuid.UUID, notification_id: uuid.UUID
    ) -> Notification | None:
        result = await db.execute(
            select(Notification).where(
                Notification.id == notification_id, Notification.user_id == user_id
            )
        )
        obj = result.scalar_one_or_none()
        if obj:
            obj.is_read = True
            await db.flush()
        return obj

    async def mark_all_read(self, db: AsyncSession, user_id: uuid.UUID) -> int:
        stmt = (
            update(Notification)
            .where(Notification.user_id == user_id, Notification.is_read == False)  # noqa: E712
            .values(is_read=True)
        )
        res = await db.execute(stmt)
        await db.flush()
        return res.rowcount

    async def delete(self, db: AsyncSession, obj: Notification) -> None:
        await db.delete(obj)
        await db.flush()


notification_repo = NotificationRepository()
