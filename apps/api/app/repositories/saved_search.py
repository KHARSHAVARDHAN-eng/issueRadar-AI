import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.saved_search import SavedSearch


class SavedSearchRepository:
    """Persistence layer for SavedSearch entity."""

    async def create(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        name: str,
        search_query: str | None,
        filters_json: dict,
    ) -> SavedSearch:
        obj = SavedSearch(
            user_id=user_id,
            name=name,
            search_query=search_query,
            filters_json=filters_json,
        )
        db.add(obj)
        await db.flush()
        return obj

    async def get_by_id(self, db: AsyncSession, search_id: uuid.UUID) -> SavedSearch | None:
        result = await db.execute(select(SavedSearch).where(SavedSearch.id == search_id))
        return result.scalar_one_or_none()

    async def get_by_user(self, db: AsyncSession, user_id: uuid.UUID) -> list[SavedSearch]:
        result = await db.execute(
            select(SavedSearch)
            .where(SavedSearch.user_id == user_id)
            .order_by(SavedSearch.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(
        self,
        db: AsyncSession,
        obj: SavedSearch,
        name: str | None = None,
        search_query: str | None = None,
        filters_json: dict | None = None,
    ) -> SavedSearch:
        if name is not None:
            obj.name = name
        if search_query is not None:
            obj.search_query = search_query
        if filters_json is not None:
            obj.filters_json = filters_json
        await db.flush()
        return obj

    async def delete(self, db: AsyncSession, obj: SavedSearch) -> None:
        await db.delete(obj)
        await db.flush()


saved_search_repo = SavedSearchRepository()
