from fastapi import APIRouter, Depends, Request

from ...config import GatewaySettings
from ...deps import get_settings, require_user
from ...infra.clients.llm_client import LLMGatewayClient

router = APIRouter()


def get_llm_client(settings: GatewaySettings = Depends(get_settings)) -> LLMGatewayClient:
    return LLMGatewayClient(
        base_url=settings.llm_gateway_url,
        service_secret=settings.polymath_service_secret,
        timeout=settings.llm_timeout,
    )


@router.post("/complete")
async def proxy_complete(
    request: Request,
    user_id: str = Depends(require_user),
    llm: LLMGatewayClient = Depends(get_llm_client),
) -> dict:
    body = await request.json()
    return await llm.complete(user_id=user_id, payload=body)


@router.get("/prompts")
async def proxy_list_prompts(
    user_id: str = Depends(require_user),
    llm: LLMGatewayClient = Depends(get_llm_client),
) -> list:
    return await llm.list_prompts(user_id=user_id)


@router.get("/usage")
async def proxy_usage(
    user_id: str = Depends(require_user),
    llm: LLMGatewayClient = Depends(get_llm_client),
) -> dict:
    return await llm.get_usage(user_id=user_id)
