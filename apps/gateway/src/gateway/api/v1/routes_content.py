from fastapi import APIRouter, Depends, Request, Response

from ...config import GatewaySettings
from ...deps import get_optional_user, get_settings, require_user
from ...infra.clients.content_client import ContentClient

router = APIRouter()


def get_content_client(settings: GatewaySettings = Depends(get_settings)) -> ContentClient:
    return ContentClient(
        base_url=settings.content_svc_url,
        service_secret=settings.polymath_service_secret,
        timeout=settings.default_timeout,
    )


# --- Public routes ---

@router.get("/posts")
async def list_posts(
    kind: str | None = None,
    tag: str | None = None,
    limit: int = 20,
    offset: int = 0,
    content: ContentClient = Depends(get_content_client),
) -> list:
    return await content.list_posts(kind=kind, tag=tag, limit=limit, offset=offset)


@router.get("/posts/{slug}")
async def get_post(
    slug: str,
    content: ContentClient = Depends(get_content_client),
) -> dict:
    return await content.get_post(slug=slug)


@router.get("/reading-log")
async def list_reading_log(
    limit: int = 50,
    content: ContentClient = Depends(get_content_client),
) -> list:
    return await content.list_reading_log(limit=limit)


# --- Authed routes ---

@router.post("/posts")
async def create_post(
    request: Request,
    user_id: str = Depends(require_user),
    content: ContentClient = Depends(get_content_client),
) -> dict:
    return await content.create_post(user_id=user_id, payload=await request.json())


@router.put("/posts/{post_id}")
async def update_post(
    post_id: str,
    request: Request,
    user_id: str = Depends(require_user),
    content: ContentClient = Depends(get_content_client),
) -> dict:
    return await content.update_post(user_id=user_id, post_id=post_id, payload=await request.json())


@router.post("/posts/{post_id}/publish")
async def publish_post(
    post_id: str,
    user_id: str = Depends(require_user),
    content: ContentClient = Depends(get_content_client),
) -> dict:
    return await content.publish_post(user_id=user_id, post_id=post_id)


@router.post("/reading-log")
async def add_reading_log(
    request: Request,
    user_id: str = Depends(require_user),
    content: ContentClient = Depends(get_content_client),
) -> dict:
    return await content.add_reading_log(user_id=user_id, payload=await request.json())
