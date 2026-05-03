import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class HabitCreate(BaseModel):
    name: str
    description: str | None = None
    cadence: str = "daily"
    target_per_period: int = 1


class HabitUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    cadence: str | None = None
    target_per_period: int | None = None


class HabitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: str
    name: str
    description: str | None
    cadence: str
    target_per_period: int
    created_at: datetime


class CheckinCreate(BaseModel):
    habit_id: uuid.UUID
    occurred_on: date | None = None
    note: str | None = None


class CheckinResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    habit_id: uuid.UUID
    user_id: str
    occurred_on: date
    count: int
    created_at: datetime


class TodoCreate(BaseModel):
    title: str
    body_md: str | None = None
    due_at: datetime | None = None
    priority: int = 3


class TodoUpdate(BaseModel):
    title: str | None = None
    body_md: str | None = None
    due_at: datetime | None = None
    priority: int | None = None
    status: str | None = None


class TodoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: str
    title: str
    body_md: str | None
    due_at: datetime | None
    priority: int
    status: str
    completed_at: datetime | None
    created_at: datetime


class StreakResponse(BaseModel):
    current: int
    longest: int


class HeatmapEntry(BaseModel):
    date: date
    count: int
