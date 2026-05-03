import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from polymath_core.errors import NotFoundError
from habits_svc.domain.services import HabitService, TodoService
from habits_svc.infra.db.models import Habit, Todo


@pytest.fixture
def habit_svc() -> HabitService:
    return HabitService()


@pytest.fixture
def todo_svc() -> TodoService:
    return TodoService()


@pytest.mark.asyncio
async def test_get_habit_raises_not_found_when_missing(habit_svc):
    session = AsyncMock()
    habit_id = uuid.uuid4()
    user_id = "user_abc123"

    with patch(
        "habits_svc.domain.services._habit_repo.get",
        new=AsyncMock(return_value=None),
    ):
        with pytest.raises(NotFoundError):
            await habit_svc.get_habit(session, habit_id, user_id)


@pytest.mark.asyncio
async def test_complete_todo_sets_status_done(todo_svc):
    session = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()

    todo_id = uuid.uuid4()
    user_id = "user_abc123"

    fake_todo = MagicMock(spec=Todo)
    fake_todo.id = todo_id
    fake_todo.user_id = user_id
    fake_todo.status = "open"
    fake_todo.completed_at = None

    async def mock_refresh(obj):
        pass

    session.refresh.side_effect = mock_refresh

    with patch(
        "habits_svc.domain.services._todo_repo.get",
        new=AsyncMock(return_value=fake_todo),
    ):
        result = await todo_svc.complete_todo(session, todo_id, user_id)

    assert result.status == "done"
    assert result.completed_at is not None
