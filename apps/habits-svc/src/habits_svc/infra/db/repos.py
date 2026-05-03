import uuid
from datetime import date, datetime, timedelta, timezone
from typing import Any

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Checkin, Habit, Todo


class HabitRepository:
    async def create(
        self,
        session: AsyncSession,
        user_id: str,
        name: str,
        description: str | None = None,
        cadence: str = "daily",
        target_per_period: int = 1,
    ) -> Habit:
        habit = Habit(
            user_id=user_id,
            name=name,
            description=description,
            cadence=cadence,
            cadence_config={},
            target_per_period=target_per_period,
        )
        session.add(habit)
        await session.flush()
        await session.refresh(habit)
        return habit

    async def get(
        self, session: AsyncSession, habit_id: uuid.UUID, user_id: str
    ) -> Habit | None:
        result = await session.execute(
            select(Habit).where(
                and_(Habit.id == habit_id, Habit.user_id == user_id)
            )
        )
        return result.scalar_one_or_none()

    async def list(self, session: AsyncSession, user_id: str) -> list[Habit]:
        result = await session.execute(
            select(Habit).where(
                and_(Habit.user_id == user_id, Habit.archived_at.is_(None))
            ).order_by(Habit.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(
        self,
        session: AsyncSession,
        habit_id: uuid.UUID,
        user_id: str,
        **fields: Any,
    ) -> Habit | None:
        habit = await self.get(session, habit_id, user_id)
        if habit is None:
            return None
        for key, value in fields.items():
            if value is not None:
                setattr(habit, key, value)
        await session.flush()
        await session.refresh(habit)
        return habit

    async def archive(
        self, session: AsyncSession, habit_id: uuid.UUID, user_id: str
    ) -> bool:
        habit = await self.get(session, habit_id, user_id)
        if habit is None:
            return False
        habit.archived_at = datetime.now(timezone.utc)
        await session.flush()
        return True


class CheckinRepository:
    async def create_or_increment(
        self,
        session: AsyncSession,
        habit_id: uuid.UUID,
        user_id: str,
        occurred_on: date,
        note: str | None = None,
    ) -> Checkin:
        result = await session.execute(
            select(Checkin).where(
                and_(
                    Checkin.habit_id == habit_id,
                    Checkin.occurred_on == occurred_on,
                )
            )
        )
        existing = result.scalar_one_or_none()
        if existing is not None:
            existing.count += 1
            if note is not None:
                existing.note = note
            await session.flush()
            await session.refresh(existing)
            return existing

        checkin = Checkin(
            habit_id=habit_id,
            user_id=user_id,
            occurred_on=occurred_on,
            count=1,
            note=note,
        )
        session.add(checkin)
        await session.flush()
        await session.refresh(checkin)
        return checkin

    async def list_for_user(
        self,
        session: AsyncSession,
        user_id: str,
        since: date,
        until: date,
    ) -> list[Checkin]:
        result = await session.execute(
            select(Checkin).where(
                and_(
                    Checkin.user_id == user_id,
                    Checkin.occurred_on >= since,
                    Checkin.occurred_on <= until,
                )
            ).order_by(Checkin.occurred_on.asc())
        )
        return list(result.scalars().all())

    async def get_streak(
        self, session: AsyncSession, habit_id: uuid.UUID, user_id: str
    ) -> dict[str, int]:
        result = await session.execute(
            select(Checkin.occurred_on)
            .where(
                and_(Checkin.habit_id == habit_id, Checkin.user_id == user_id)
            )
            .order_by(Checkin.occurred_on.desc())
        )
        rows = [r for (r,) in result.all()]

        if not rows:
            return {"current": 0, "longest": 0}

        # Calculate current streak (consecutive days ending today or yesterday)
        today = date.today()
        current = 0
        expected = today
        for d in rows:
            if d == expected:
                current += 1
                expected = d - timedelta(days=1)
            elif d == today - timedelta(days=1) and current == 0:
                # Allow streak that ended yesterday
                current += 1
                expected = d - timedelta(days=1)
            else:
                break

        # Calculate longest streak
        sorted_dates = sorted(set(rows))
        longest = 0
        run = 0
        prev: date | None = None
        for d in sorted_dates:
            if prev is None or d == prev + timedelta(days=1):
                run += 1
            else:
                run = 1
            if run > longest:
                longest = run
            prev = d

        return {"current": current, "longest": longest}


class TodoRepository:
    async def create(
        self,
        session: AsyncSession,
        user_id: str,
        title: str,
        body_md: str | None = None,
        due_at: datetime | None = None,
        priority: int = 3,
    ) -> Todo:
        todo = Todo(
            user_id=user_id,
            title=title,
            body_md=body_md,
            due_at=due_at,
            priority=priority,
        )
        session.add(todo)
        await session.flush()
        await session.refresh(todo)
        return todo

    async def get(
        self, session: AsyncSession, todo_id: uuid.UUID, user_id: str
    ) -> Todo | None:
        result = await session.execute(
            select(Todo).where(and_(Todo.id == todo_id, Todo.user_id == user_id))
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        session: AsyncSession,
        user_id: str,
        status: str | None = None,
    ) -> list[Todo]:
        query = select(Todo).where(Todo.user_id == user_id)
        if status is not None:
            query = query.where(Todo.status == status)
        query = query.order_by(Todo.priority.asc(), Todo.created_at.desc())
        result = await session.execute(query)
        return list(result.scalars().all())

    async def update(
        self,
        session: AsyncSession,
        todo_id: uuid.UUID,
        user_id: str,
        **fields: Any,
    ) -> Todo | None:
        todo = await self.get(session, todo_id, user_id)
        if todo is None:
            return None
        for key, value in fields.items():
            if value is not None:
                setattr(todo, key, value)
        await session.flush()
        await session.refresh(todo)
        return todo
