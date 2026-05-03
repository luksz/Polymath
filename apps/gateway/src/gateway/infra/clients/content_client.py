from .base import ServiceClient


class ContentClient(ServiceClient):
    async def list_posts(self, kind: str | None = None, tag: str | None = None, limit: int = 20, offset: int = 0) -> list:
        params: dict = {"limit": limit, "offset": offset}
        if kind:
            params["kind"] = kind
        if tag:
            params["tag"] = tag
        return await self.get("/v1/posts", params=params)

    async def get_post(self, slug: str) -> dict:
        return await self.get(f"/v1/posts/{slug}")

    async def create_post(self, user_id: str, payload: dict) -> dict:
        return await self.post("/v1/posts", user_id=user_id, json=payload)

    async def update_post(self, user_id: str, post_id: str, payload: dict) -> dict:
        return await self.put(f"/v1/posts/{post_id}", user_id=user_id, json=payload)

    async def publish_post(self, user_id: str, post_id: str) -> dict:
        return await self.post(f"/v1/posts/{post_id}/publish", user_id=user_id)

    async def list_reading_log(self, limit: int = 50) -> list:
        return await self.get("/v1/reading-log", params={"limit": limit})

    async def add_reading_log(self, user_id: str, payload: dict) -> dict:
        return await self.post("/v1/reading-log", user_id=user_id, json=payload)
