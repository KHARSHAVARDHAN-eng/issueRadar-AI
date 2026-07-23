import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.repository import RepositoryRead


class SyncJobRead(BaseModel):
    id: uuid.UUID
    repository_id: uuid.UUID
    status: str
    started_at: datetime | None
    finished_at: datetime | None
    issues_processed: int
    errors: str | None
    created_at: datetime
    updated_at: datetime
    repository: RepositoryRead | None = None

    model_config = ConfigDict(from_attributes=True)
