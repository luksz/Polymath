import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class DigestPaperResponse(BaseModel):
    id: uuid.UUID
    arxiv_id: str
    title: str
    authors: list[str]
    arxiv_url: str
    relevance_score: int
    summary_headline: str
    summary_body: str
    key_insight: str
    why_it_matters: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DigestResponse(BaseModel):
    id: uuid.UUID
    for_date: date
    topic_tags: list[str]
    status: str
    created_at: datetime
    papers: list[DigestPaperResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class DigestListItem(BaseModel):
    id: uuid.UUID
    for_date: date
    status: str
    paper_count: int
    created_at: datetime

    model_config = {"from_attributes": True}
