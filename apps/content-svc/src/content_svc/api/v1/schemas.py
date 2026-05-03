import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class PostCreate(BaseModel):
    slug: str
    kind: str
    title: str
    body_mdx: str
    summary: str | None = None
    tags: list[str] = []
    cover_image_url: str | None = None


class PostUpdate(BaseModel):
    title: str | None = None
    body_mdx: str | None = None
    summary: str | None = None
    tags: list[str] | None = None
    cover_image_url: str | None = None
    status: str | None = None


class PostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    kind: str
    title: str
    summary: str | None
    tags: list[str]
    status: str
    published_at: datetime | None
    cover_image_url: str | None
    reading_minutes: int | None
    created_at: datetime
    updated_at: datetime


class PostDetailResponse(PostResponse):
    body_mdx: str


class ReadingLogCreate(BaseModel):
    title: str
    url: str | None = None
    source: str | None = None
    finished_on: date | None = None
    rating: int | None = None
    notes_md: str | None = None
    tags: list[str] = []


class ReadingLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: str
    title: str
    url: str | None
    source: str | None
    finished_on: date | None
    rating: int | None
    notes_md: str | None
    tags: list[str]
    created_at: datetime
