import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.issue import IssueRead


class NotificationRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    issue_id: uuid.UUID | None
    saved_search_id: uuid.UUID | None
    type: str
    title: str
    message: str
    is_read: bool
    created_at: datetime
    issue: IssueRead | None = None

    model_config = ConfigDict(from_attributes=True)
