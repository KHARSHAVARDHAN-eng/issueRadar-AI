import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.repository import Repository


class RepositoryRepository:
    """Persistence layer for Repository database operations."""

    async def create(self, db: AsyncSession, repository: Repository) -> Repository:
        db.add(repository)
        await db.commit()
        await db.refresh(repository)
        return repository

    async def get_by_id(self, db: AsyncSession, repository_id: uuid.UUID) -> Repository | None:
        result = await db.execute(select(Repository).where(Repository.id == repository_id))
        return result.scalar_one_or_none()

    async def get_by_user(self, db: AsyncSession, user_id: uuid.UUID) -> Sequence[Repository]:
        result = await db.execute(
            select(Repository)
            .where(Repository.added_by_id == user_id)
            .order_by(Repository.created_at.desc())
        )
        return result.scalars().all()

    async def get_by_user_and_github_id(
        self, db: AsyncSession, user_id: uuid.UUID, github_id: int
    ) -> Repository | None:
        result = await db.execute(
            select(Repository).where(
                Repository.added_by_id == user_id,
                Repository.github_id == github_id,
            )
        )
        return result.scalar_one_or_none()

    async def delete(self, db: AsyncSession, repository: Repository) -> None:
        await db.delete(repository)
        await db.commit()


repository_repo = RepositoryRepository()
