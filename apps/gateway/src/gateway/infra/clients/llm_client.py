from .base import ServiceClient


class LLMGatewayClient(ServiceClient):
    async def complete(self, user_id: str, payload: dict) -> dict:
        return await self.post("/v1/complete", user_id=user_id, json=payload)

    async def list_prompts(self, user_id: str) -> list:
        return await self.get("/v1/prompts", user_id=user_id)

    async def get_usage(self, user_id: str) -> dict:
        return await self.get("/v1/usage", user_id=user_id)
