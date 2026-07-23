from pydantic import BaseModel, ConfigDict

from app.schemas.issue import IssueRead


class PaginatedIssuesResponse(BaseModel):
    items: list[IssueRead]
    total: int
    page: int
    page_size: int
    pages: int

    model_config = ConfigDict(from_attributes=True)
