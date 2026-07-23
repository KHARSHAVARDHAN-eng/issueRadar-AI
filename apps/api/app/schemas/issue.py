import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.analysis import IssueAnalysisRead
from app.schemas.score import IssueScoreRead


class LabelRead(BaseModel):
    id: uuid.UUID
    github_id: int | None = None
    name: str
    color: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CommentRead(BaseModel):
    id: uuid.UUID
    github_id: int
    body: str
    author_username: str | None = None
    author_avatar_url: str | None = None
    github_created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IssueRead(BaseModel):
    id: uuid.UUID
    github_id: int
    number: int
    title: str
    body: str | None = None
    state: str
    author_username: str | None = None
    author_avatar_url: str | None = None
    html_url: str
    comments_count: int
    is_pull_request: bool
    repository_id: uuid.UUID
    labels: list[LabelRead] = []
    score: IssueScoreRead | None = None
    analysis: IssueAnalysisRead | None = None
    github_created_at: datetime
    github_updated_at: datetime
    github_closed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class IssueDetailRead(IssueRead):
    comments: list[CommentRead] = []

    model_config = ConfigDict(from_attributes=True)
