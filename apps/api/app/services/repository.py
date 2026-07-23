import logging
import re
import uuid
from collections.abc import Sequence

import httpx
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decrypt_token
from app.models.repository import Repository
from app.models.user import User
from app.repositories.repository import repository_repo

logger = logging.getLogger(__name__)


class RepositoryService:
    """Business logic service for GitHub Repository management."""

    @staticmethod
    def parse_owner_name(input_str: str) -> tuple[str, str]:
        """Extract owner and repo name from 'owner/name' or GitHub URLs."""
        cleaned = input_str.strip()

        # Match URLs like https://github.com/owner/name or github.com/owner/name
        url_match = re.search(r"github\.com/([^/]+)/([^/\s?#]+)", cleaned)
        if url_match:
            owner, name = url_match.group(1), url_match.group(2)
        else:
            # Match owner/name format
            parts = [p for p in cleaned.split("/") if p]
            if len(parts) == 2:
                owner, name = parts[0], parts[1]
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Invalid repository format. Please specify 'owner/name' "
                        "or a valid GitHub URL."
                    ),
                )

        # Strip .git extension if present
        if name.endswith(".git"):
            name = name[:-4]

        return owner, name

    async def fetch_github_metadata(self, owner: str, name: str, github_token: str) -> dict:
        """Fetch repository details from the official GitHub REST API."""
        headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if github_token:
            headers["Authorization"] = f"Bearer {github_token}"

        url = f"https://api.github.com/repos/{owner}/{name}"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)

            if response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=(
                        f"Repository '{owner}/{name}' not found on GitHub "
                        "or private without access."
                    ),
                )
            elif response.status_code != 200:
                logger.error(
                    f"GitHub REST API error for {owner}/{name}: "
                    f"{response.status_code} {response.text}"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to fetch metadata from GitHub (HTTP {response.status_code})",
                )

            return response.json()

    async def add_repository(self, db: AsyncSession, user: User, url_or_name: str) -> Repository:
        """Validate repository against GitHub REST API and persist to database."""
        owner, name = self.parse_owner_name(url_or_name)
        github_token = decrypt_token(user.encrypted_github_token)

        meta = await self.fetch_github_metadata(owner, name, github_token)

        github_id = meta.get("id")
        full_name = meta.get("full_name", f"{owner}/{name}")

        if not github_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GitHub API returned invalid metadata missing repository ID",
            )

        # Check for duplicates per user
        existing = await repository_repo.get_by_user_and_github_id(db, user.id, github_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Repository '{full_name}' is already added to your monitor list.",
            )

        repo = Repository(
            github_id=github_id,
            owner=meta.get("owner", {}).get("login", owner),
            name=meta.get("name", name),
            full_name=full_name,
            description=meta.get("description"),
            language=meta.get("language"),
            default_branch=meta.get("default_branch", "main"),
            stars=meta.get("stargazers_count", 0),
            forks=meta.get("forks_count", 0),
            private=meta.get("private", False),
            added_by_id=user.id,
        )

        return await repository_repo.create(db, repo)

    async def list_repositories(self, db: AsyncSession, user: User) -> Sequence[Repository]:
        """Get all repositories monitored by the specified user."""
        return await repository_repo.get_by_user(db, user.id)

    async def get_repository(
        self, db: AsyncSession, user: User, repository_id: uuid.UUID
    ) -> Repository:
        """Retrieve a specific repository owned by the user."""
        repo = await repository_repo.get_by_id(db, repository_id)
        if not repo or repo.added_by_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Repository not found",
            )
        return repo

    async def delete_repository(
        self, db: AsyncSession, user: User, repository_id: uuid.UUID
    ) -> None:
        """Remove a repository from the user's monitor list."""
        repo = await self.get_repository(db, user, repository_id)
        await repository_repo.delete(db, repo)


repository_service = RepositoryService()
