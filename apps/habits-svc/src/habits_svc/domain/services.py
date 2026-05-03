import uuid
from datetime import date, datetime, timezone

import structlog

from polymath_core.errors import NotFoundError
from sqlalchemy.ext.asyncio import AsyncSession

from ..infra.db.models import Checkin, Habit, Todo
from ..infra.db.repos import CheckinRepository, HabitRepository, TodoRepository

log = structlog.get_logger(__name__)

_habit_repo = HabitRepository()
_checkin_repo = CheckinRepository()
_todo_repo = TodoRepository()


class HabitService:
    async def create_habit(
        self,
        session: AsyncSession,
        user_id: str,
        name: str,
        description: str | None = None,
        cadence: str = "daily",
        target_per_period: int = 1,
    ) -> Habit:
        habit = await _habit_repo.create(
            session,
            user_id=user_id,
            name=name,
            description=description,
            cadence=cadence,
            target_per_period=target_per_period,
        )
        log.info("habit.created", habit_id=str(habit.id), user_id=user_id)
        return habit

    async def get_habit(
        self, session: AsyncSession, habit_id: uuid.UUID, user_id: str
    ) -> Habit:
        habit = await _habit_repo.get(session, habit_id, user_id)
        if habit is None:
            raise NotFoundError(f"Habit {habit_id} not found")
        return habit

    async def list_habits(self, session: AsyncSession, user_id: str) -> list[Habit]:
        return await _habit_repo.list(session, user_id)

    async def update_habit(
        self,
        session: AsyncSession,
        habit_id: uuid.UUID,
        user_id: str,
        **fields: object,
    ) -> Habit:
        habit = await _habit_repo.update(session, habit_id, user_id, **fields)
        if habit is None:
            raise NotFoundError(f"Habit {habit_id} not found")
        log.info("habit.updated", habit_id=str(habit_id), user_id=user_id)
        return habit

    async def archive_habit(
        self, session: AsyncSession, habit_id: uuid.UUID, user_id: str
    ) -> None:
        archived = await _habit_repo.archive(session, habit_id, user_id)
        if not archived:
            raise NotFoundError(f"Habit {habit_id} not found")
        log.info("habit.archived", habit_id=str(habit_id), user_id=user_id)

    async def checkin_today(
        self,
        session: AsyncSession,
        habit_id: uuid.UUID,
        user_id: str,
        note: str | None = None,
    ) -> Checkin:
        today = date.today()
        checkin = await _checkin_repo.create_or_increment(
            session, habit_id, user_id, today, note=note
        )
        log.info(
            "habit.checkin",
            habit_id=str(habit_id),
            user_id=user_id,
            occurred_on=str(today),
            count=checkin.count,
        )
        return checkin

    async def get_heatmap(
        self, session: AsyncSession, user_id: str, year: int
    ) -> list[dict[str, object]]:
        since = date(year, 1, 1)
        until = date(year, 12, 31)
        checkins = await _checkin_repo.list_for_user(session, user_id, since, until)
        # Aggregate by date across all habits
        totals: dict[date, int] = {}
        for c in checkins:
            totals[c.occurred_on] = totals.get(c.occurred_on, 0) + c.count
        return [{"date": d, "count": count} for d, count in sorted(totals.items())]

    async def get_streak(
        self, session: AsyncSession, habit_id: uuid.UUID, user_id: str
    ) -> dict[str, int]:
        return await _checkin_repo.get_streak(session, habit_id, user_id)


class TodoService:
    async def create_todo(
        self,
        session: AsyncSession,
        user_id: str,
        title: str,
        body_md: str | None = None,
        due_at: datetime | None = None,
        priority: int = 3,
    ) -> Todo:
        todo = await _todo_repo.create(
            session,
            user_id=user_id,
            title=title,
            body_md=body_md,
            due_at=due_at,
            priority=priority,
        )
        log.info("todo.created", todo_id=str(todo.id), user_id=user_id)
        return todo

    async def get_todo(
        self, session: AsyncSession, todo_id: uuid.UUID, user_id: str
    ) -> Todo:
        todo = await _todo_repo.get(session, todo_id, user_id)
        if todo is None:
            raise NotFoundError(f"Todo {todo_id} not found")
        return todo

    async def list_todos(
        self,
        session: AsyncSession,
        user_id: str,
        status: str | None = None,
    ) -> list[Todo]:
        return await _todo_repo.list(session, user_id, status=status)

    async def update_todo(
        self,
        session: AsyncSession,
        todo_id: uuid.UUID,
        user_id: str,
        **fields: object,
    ) -> Todo:
        todo = await _todo_repo.update(session, todo_id, user_id, **fields)
        if todo is None:
            raise NotFoundError(f"Todo {todo_id} not found")
        log.info("todo.updated", todo_id=str(todo_id), user_id=user_id)
        return todo

    async def complete_todo(
        self, session: AsyncSession, todo_id: uuid.UUID, user_id: str
    ) -> Todo:
        todo = await _todo_repo.get(session, todo_id, user_id)
        if todo is None:
            raise NotFoundError(f"Todo {todo_id} not found")
        todo.status = "done"
        todo.completed_at = datetime.now(timezone.utc)
        await session.flush()
        await session.refresh(todo)
        log.info("todo.completed", todo_id=str(todo_id), user_id=user_id)
        return todo
