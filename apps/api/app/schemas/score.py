import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IssueScoreRead(BaseModel):
    id: uuid.UUID
    issue_id: uuid.UUID
    score: float
    recommendation: str
    rule_breakdown: dict[str, float]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
