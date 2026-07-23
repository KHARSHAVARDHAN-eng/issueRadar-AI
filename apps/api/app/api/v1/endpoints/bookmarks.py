import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models.bookmark import Bookmark
from app.models.user import User
from app.repositories.bookmark import bookmark_repo
from app.repositories.issue import issue_repo
from app.schemas.bookmark import BookmarkCreate, BookmarkRead

router = APIRouter()


@router.post(
    "",
    response_model=BookmarkRead,
    status_code=status.HTTP_201_CREATED,
    summary="Bookmark an issue",
)
async def create_bookmark(
    body: BookmarkCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    issue = await issue_repo.get_by_id(db, body.issue_id)
    if not issue or issue.repository.added_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found",
        )
    obj = await bookmark_repo.create_or_update(
        db, user_id=current_user.id, issue_id=body.issue_id, notes=body.notes
    )
    await db.commit()
    return obj


@router.get(
    "",
    response_model=list[BookmarkRead],
    summary="List bookmarked issues for current user",
)
async def list_bookmarks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await bookmark_repo.get_by_user(db, current_user.id)


@router.delete(
    "/{bookmark_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove bookmark",
)
async def delete_bookmark(
    bookmark_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Bookmark).where(
        Bookmark.user_id == current_user.id,
        or_(Bookmark.id == bookmark_id, Bookmark.issue_id == bookmark_id),
    )
    res = await db.execute(stmt)
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found",
        )
    await bookmark_repo.delete(db, obj)
    await db.commit()
