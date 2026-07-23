import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models.user import User
from app.repositories.saved_search import saved_search_repo
from app.schemas.saved_search import SavedSearchCreate, SavedSearchRead, SavedSearchUpdate

router = APIRouter()


@router.post(
    "",
    response_model=SavedSearchRead,
    status_code=status.HTTP_201_CREATED,
    summary="Save a search configuration",
)
async def create_saved_search(
    body: SavedSearchCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    obj = await saved_search_repo.create(
        db,
        user_id=current_user.id,
        name=body.name,
        search_query=body.search_query,
        filters_json=body.filters_json,
    )
    await db.commit()
    return obj


@router.get(
    "",
    response_model=list[SavedSearchRead],
    summary="List saved searches for current user",
)
async def list_saved_searches(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await saved_search_repo.get_by_user(db, current_user.id)


@router.put(
    "/{search_id}",
    response_model=SavedSearchRead,
    summary="Update saved search configuration",
)
async def update_saved_search(
    search_id: uuid.UUID,
    body: SavedSearchUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    obj = await saved_search_repo.get_by_id(db, search_id)
    if not obj or obj.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved search not found",
        )
    updated = await saved_search_repo.update(
        db, obj, name=body.name, search_query=body.search_query, filters_json=body.filters_json
    )
    await db.commit()
    return updated


@router.delete(
    "/{search_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete saved search",
)
async def delete_saved_search(
    search_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    obj = await saved_search_repo.get_by_id(db, search_id)
    if not obj or obj.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved search not found",
        )
    await saved_search_repo.delete(db, obj)
    await db.commit()
