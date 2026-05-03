from fastapi import APIRouter, Depends, Request, Response

from ...config import GatewaySettings
from ...deps import get_settings, require_user
from ...infra.clients.habits_client import HabitsClient

router = APIRouter()


def get_habits_client(settings: GatewaySettings = Depends(get_settings)) -> HabitsClient:
    return HabitsClient(
        base_url=settings.habits_svc_url,
        service_secret=settings.polymath_service_secret,
        timeout=settings.default_timeout,
    )


@router.get("")
async def list_habits(
    user_id: str = Depends(require_user),
    habits: HabitsClient = Depends(get_habits_client),
) -> list:
    return await habits.list_habits(user_id=user_id)


@router.post("")
async def create_habit(
    request: Request,
    user_id: str = Depends(require_user),
    habits: HabitsClient = Depends(get_habits_client),
) -> dict:
    return await habits.create_habit(user_id=user_id, payload=await request.json())


@router.get("/heatmap")
async def get_heatmap(
    year: int,
    user_id: str = Depends(require_user),
    habits: HabitsClient = Depends(get_habits_client),
) -> list:
    return await habits.get_heatmap(user_id=user_id, year=year)


@router.get("/{habit_id}")
async def get_habit(
    habit_id: str,
    user_id: str = Depends(require_user),
    habits: HabitsClient = Depends(get_habits_client),
) -> dict:
    return await habits.get_habit(user_id=user_id, habit_id=habit_id)


@router.get("/{habit_id}/streak")
async def get_streak(
    habit_id: str,
    user_id: str = Depends(require_user),
    habits: HabitsClient = Depends(get_habits_client),
) -> dict:
    return await habits.get_streak(user_id=user_id, habit_id=habit_id)


@router.post("/checkins")
async def checkin(
    request: Request,
    user_id: str = Depends(require_user),
    habits: HabitsClient = Depends(get_habits_client),
) -> dict:
    return await habits.checkin(user_id=user_id, payload=await request.json())


# Todos sub-resource
todos_router = APIRouter()


@todos_router.get("")
async def list_todos(
    status: str | None = None,
    user_id: str = Depends(require_user),
    habits: HabitsClient = Depends(get_habits_client),
) -> list:
    return await habits.list_todos(user_id=user_id, status=status)


@todos_router.post("")
async def create_todo(
    request: Request,
    user_id: str = Depends(require_user),
    habits: HabitsClient = Depends(get_habits_client),
) -> dict:
    return await habits.create_todo(user_id=user_id, payload=await request.json())


@todos_router.post("/{todo_id}/complete", status_code=204)
async def complete_todo(
    todo_id: str,
    user_id: str = Depends(require_user),
    habits: HabitsClient = Depends(get_habits_client),
) -> Response:
    await habits.complete_todo(user_id=user_id, todo_id=todo_id)
    return Response(status_code=204)
