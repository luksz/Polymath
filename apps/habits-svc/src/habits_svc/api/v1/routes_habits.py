import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...deps import get_db
from ...domain.services import HabitService, TodoService
from ...infra.db.repos import CheckinRepository
from .schemas import (
    CheckinCreate,
    CheckinResponse,
    HabitCreate,
    HabitResponse,
    HabitUpdate,
    HeatmapEntry,
    StreakResponse,
    TodoCreate,
    TodoResponse,
    TodoUpdate,
)

habits_router = APIRouter(prefix="/v1/habits", tags=["habits"])
todos_router = APIRouter(prefix="/v1/todos", tags=["todos"])

_habit_svc = HabitService()
_todo_svc = TodoService()


def _user_id_header(
    x_polymath_user_id: Annotated[str, Header(alias="X-Polymath-User-Id")],
) -> str:
    return x_polymath_user_id


@habits_router.get("/heatmap", response_model=list[HeatmapEntry])
async def get_heatmap(
    year: int = date.today().year,
    user_id: str = Depends(_user_id_header),
    db: AsyncSession = Depends(get_db),
) -> list[HeatmapEntry]:
    entries = await _habit_svc.get_heatmap(db, user_id, year)
    return [HeatmapEntry(date=e["date"], count=e["count"]) for e in entries]  # type: ignore[arg-type]


@habits_router.get("/", response_model=list[HabitResponse])
async def list_habits(
    user_id: str = Depends(_user_id_header),
    db: AsyncSession = Depends(get_db),
) -> list[HabitResponse]:
    habits = await _habit_svc.list_habits(db, user_id)
    return [HabitResponse.model_validate(h) for h in habits]


@habits_router.post("/", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
async def create_habit(
    body: HabitCreate,
    user_id: str = Depends(_user_id_header),
    db: AsyncSession = Depends(get_db),
) -> HabitResponse:
    habit = await _habit_svc.create_habit(
        db,
        user_id=user_id,
        name=body.name,
        description=body.description,
        cadence=body.cadence,
        target_per_period=body.target_per_period,
    )
    return HabitResponse.model_validate(habit)


@habits_router.get("/{habit_id}", response_model=HabitResponse)
async def get_habit(
    habit_id: uuid.UUID,
    user_id: str = Depends(_user_id_header),
    db: AsyncSession = Depends(get_db),
) -> HabitResponse:
    habit = await _habit_svc.get_habit(db, habit_id, user_id)
    return HabitResponse.model_validate(habit)


@habits_router.put("/{habit_id}", response_model=HabitResponse)
async def update_habit(
    habit_id: uuid.UUID,
    body: HabitUpdate,
    user_id: str = Depends(_user_id_header),
    db: AsyncSession = Depends(get_db),
) -> HabitResponse:
    fields = body.model_dump(exclude_unset=True)
    habit = await _habit_svc.update_habit(db, habit_id, user_id, **fields)
    return HabitResponse.model_validate(habit)


@habits_router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def archive_habit(
    habit_id: uuid.UUID,
    user_id: str = Depends(_user_id_header),
    db: AsyncSession = Depends(get_db),
) -> Response:
    await _habit_svc.archive_habit(db, habit_id, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@habits_router.get("/{habit_id}/streak", response_model=StreakResponse)
async def get_streak(
    habit_id: uuid.UUID,
    user_id: str = Depends(_user_id_header),
    db: AsyncSession = Depends(get_db),
) -> StreakResponse:
    streak = await _habit_svc.get_streak(db, habit_id, user_id)
    return StreakResponse(**streak)


@habits_router.post("/checkins", response_model=CheckinResponse, status_code=status.HTTP_201_CREATED)
async def create_checkin(
    body: CheckinCreate,
    user_id: str = Depends(_user_id_header),
    db: AsyncSession = Depends(get_db),
) -> CheckinResponse:
    if body.occurred_on is not None:
        repo = CheckinRepository()
        checkin = await repo.create_or_increment(
            db, body.habit_id, user_id, body.occurred_on, note=body.note
        )
    else:
        checkin = await _habit_svc.checkin_today(
            db, body.habit_id, user_id, note=body.note
        )
    return CheckinResponse.model_validate(checkin)


# ---- Todos ----

@todos_router.get("/", response_model=list[TodoResponse])
async def list_todos(
    status_filter: str | None = None,
    user_id: str = Depends(_user_id_header),
    db: AsyncSession = Depends(get_db),
) -> list[TodoResponse]:
    todos = await _todo_svc.list_todos(db, user_id, status=status_filter)
    return [TodoResponse.model_validate(t) for t in todos]


@todos_router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    body: TodoCreate,
    user_id: str = Depends(_user_id_header),
    db: AsyncSession = Depends(get_db),
) -> TodoResponse:
    todo = await _todo_svc.create_todo(
        db,
        user_id=user_id,
        title=body.title,
        body_md=body.body_md,
        due_at=body.due_at,
        priority=body.priority,
    )
    return TodoResponse.model_validate(todo)


@todos_router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(
    todo_id: uuid.UUID,
    user_id: str = Depends(_user_id_header),
    db: AsyncSession = Depends(get_db),
) -> TodoResponse:
    todo = await _todo_svc.get_todo(db, todo_id, user_id)
    return TodoResponse.model_validate(todo)


@todos_router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: uuid.UUID,
    body: TodoUpdate,
    user_id: str = Depends(_user_id_header),
    db: AsyncSession = Depends(get_db),
) -> TodoResponse:
    fields = body.model_dump(exclude_unset=True)
    todo = await _todo_svc.update_todo(db, todo_id, user_id, **fields)
    return TodoResponse.model_validate(todo)


@todos_router.post("/{todo_id}/complete", status_code=status.HTTP_204_NO_CONTENT)
async def complete_todo(
    todo_id: uuid.UUID,
    user_id: str = Depends(_user_id_header),
    db: AsyncSession = Depends(get_db),
) -> Response:
    await _todo_svc.complete_todo(db, todo_id, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
