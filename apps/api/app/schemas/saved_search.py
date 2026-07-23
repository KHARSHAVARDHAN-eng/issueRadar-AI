import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SavedSearchCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    search_query: str | None = None
    filters_json: dict = Field(default_factory=dict)


class SavedSearchUpdate(BaseModel):
    name: str | None = None
    search_query: str | None = None
    filters_json: dict | None = None


class SavedSearchRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    search_query: str | None
    filters_json: dict
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
