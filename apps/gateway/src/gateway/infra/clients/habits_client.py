from .base import ServiceClient


class HabitsClient(ServiceClient):
    async def list_habits(self, user_id: str) -> list:
        return await self.get("/v1/habits", user_id=user_id)

    async def create_habit(self, user_id: str, payload: dict) -> dict:
        return await self.post("/v1/habits", user_id=user_id, json=payload)

    async def get_habit(self, user_id: str, habit_id: str) -> dict:
        return await self.get(f"/v1/habits/{habit_id}", user_id=user_id)

    async def get_streak(self, user_id: str, habit_id: str) -> dict:
        return await self.get(f"/v1/habits/{habit_id}/streak", user_id=user_id)

    async def get_heatmap(self, user_id: str, year: int) -> list:
        return await self.get("/v1/habits/heatmap", user_id=user_id, params={"year": year})

    async def checkin(self, user_id: str, payload: dict) -> dict:
        return await self.post("/v1/habits/checkins", user_id=user_id, json=payload)

    async def list_todos(self, user_id: str, status: str | None = None) -> list:
        params = {"status": status} if status else {}
        return await self.get("/v1/todos", user_id=user_id, params=params)

    async def create_todo(self, user_id: str, payload: dict) -> dict:
        return await self.post("/v1/todos", user_id=user_id, json=payload)

    async def complete_todo(self, user_id: str, todo_id: str) -> None:
        await self.post(f"/v1/todos/{todo_id}/complete", user_id=user_id)
