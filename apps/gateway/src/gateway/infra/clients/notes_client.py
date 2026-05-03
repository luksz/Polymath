from .base import ServiceClient


class NotesClient(ServiceClient):
    async def list_notes(self, user_id: str, q: str | None = None, tag: str | None = None, limit: int = 20, offset: int = 0) -> dict:
        params: dict = {"limit": limit, "offset": offset}
        if q:
            params["q"] = q
        if tag:
            params["tag"] = tag
        return await self.get("/v1/notes", user_id=user_id, params=params)

    async def create_note(self, user_id: str, payload: dict) -> dict:
        return await self.post("/v1/notes", user_id=user_id, json=payload)

    async def get_note(self, user_id: str, note_id: str) -> dict:
        return await self.get(f"/v1/notes/{note_id}", user_id=user_id)

    async def update_note(self, user_id: str, note_id: str, payload: dict) -> dict:
        return await self.put(f"/v1/notes/{note_id}", user_id=user_id, json=payload)

    async def delete_note(self, user_id: str, note_id: str) -> None:
        await self.delete(f"/v1/notes/{note_id}", user_id=user_id)

    async def search_notes(self, user_id: str, payload: dict) -> list:
        return await self.post("/v1/notes/search", user_id=user_id, json=payload)
