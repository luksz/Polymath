import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class Actor(BaseModel):
    type: str  # 'user' | 'system' | 'job'
    id: str


class EventEnvelope(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str  # e.g. 'notes.note.created'
    version: int = 1
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    actor: Actor
    data: dict[str, Any]

    def to_topic(self) -> str:
        return self.event_type
