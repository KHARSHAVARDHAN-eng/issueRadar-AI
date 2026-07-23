import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models.notification import Notification
from app.models.user import User
from app.repositories.notification import notification_repo
from app.schemas.notification import NotificationRead

router = APIRouter()


@router.get(
    "",
    response_model=list[NotificationRead],
    summary="List notifications for current user",
)
async def list_notifications(
    unread_only: bool = Query(False, description="Filter only unread notifications"),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await notification_repo.get_by_user(
        db, current_user.id, unread_only=unread_only, limit=limit
    )


@router.put(
    "/{notification_id}/read",
    response_model=NotificationRead,
    summary="Mark notification as read",
)
async def mark_notification_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    obj = await notification_repo.mark_read(db, current_user.id, notification_id)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    await db.commit()
    return obj


@router.post(
    "/read-all",
    summary="Mark all notifications as read",
)
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    count = await notification_repo.mark_all_read(db, current_user.id)
    await db.commit()
    return {"message": f"Marked {count} notifications as read", "marked_count": count}


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete notification",
)
async def delete_notification(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(
        select(Notification).where(
            Notification.id == notification_id, Notification.user_id == current_user.id
        )
    )
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    await notification_repo.delete(db, obj)
    await db.commit()
