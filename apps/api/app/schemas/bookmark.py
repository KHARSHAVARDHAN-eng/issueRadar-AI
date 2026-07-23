import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.issue import IssueRead


class BookmarkCreate(BaseModel):
    issue_id: uuid.UUID
    notes: str | None = None


class BookmarkRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    issue_id: uuid.UUID
    notes: str | None
    created_at: datetime
    issue: IssueRead | None = None

    model_config = ConfigDict(from_attributes=True)
