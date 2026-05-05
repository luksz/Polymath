from .base import ServiceClient


class DigestClient(ServiceClient):
    async def list_digests(self, user_id: str) -> list:
        return await self.get("/v1/digests", user_id=user_id)

    async def get_today(self, user_id: str) -> dict:
        return await self.get("/v1/digests/today", user_id=user_id)

    async def get_by_date(self, user_id: str, date: str) -> dict:
        return await self.get(f"/v1/digests/{date}", user_id=user_id)

    async def trigger_run(self, user_id: str) -> dict:
        return await self.post("/v1/digests/run", user_id=user_id)
