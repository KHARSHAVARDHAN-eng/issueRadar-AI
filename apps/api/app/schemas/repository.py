import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class RepositoryCreate(BaseModel):
    url_or_name: str

    @field_validator("url_or_name")
    @classmethod
    def validate_input(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Repository input cannot be empty")
        return cleaned


class RepositoryRead(BaseModel):
    id: uuid.UUID
    github_id: int
    owner: str
    name: str
    full_name: str
    description: str | None = None
    language: str | None = None
    default_branch: str
    stars: int
    forks: int
    private: bool
    added_by_id: uuid.UUID

    # Sync Status Fields
    last_sync_started_at: datetime | None = None
    last_sync_completed_at: datetime | None = None
    sync_status: str
    sync_error: str | None = None
    open_issues_count: int
    closed_issues_count: int
    total_issues_count: int

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
