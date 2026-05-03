import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    title: str
    body_md: str
    tags: list[str] = Field(default_factory=list)


class NoteUpdate(BaseModel):
    title: str | None = None
    body_md: str | None = None
    tags: list[str] | None = None


class NoteResponse(BaseModel):
    id: uuid.UUID
    user_id: str
    title: str
    body_md: str
    tags: list[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NoteSearchRequest(BaseModel):
    query: str
    mode: Literal["fts", "semantic", "hybrid"] = "fts"


class NoteListResponse(BaseModel):
    items: list[NoteResponse]
    total: int
